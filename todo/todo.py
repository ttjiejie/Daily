import json
import argparse
from typing import List

# 颜色常量
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

FILE_NAME = "todo.json"


def load_tasks() -> List[dict]:
    """加载任务列表并处理异常"""
    try:
        with open(FILE_NAME, "r", encoding="GBK") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError:
        print(f"{RED}错误：文件 {FILE_NAME} 格式错误，已重置{RESET}")
        return []


def save_tasks(tasks: List[dict]):
    """保存任务列表并处理异常"""
    try:
        with open(FILE_NAME, "w", encoding="GBK") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except PermissionError:
        print(f"{RED}错误：没有文件写入权限{RESET}")


def add_tasks(task_texts: List[str]):
    """批量添加任务（优化IO效率）"""
    tasks = load_tasks()
    start_id = max(task["id"] for task in tasks) + 1 if tasks else 1
    new_tasks = []

    for idx, text in enumerate(task_texts, start=start_id):
        new_tasks.append({
            "id": idx,
            "task": text.strip(),
            "done": False
        })

    tasks.extend(new_tasks)
    save_tasks(tasks)

    if len(new_tasks) == 1:
        print(f"{GREEN}✓ 添加成功！ID：{new_tasks[0]['id']}{RESET}")
    else:
        ids = ", ".join(str(t["id"]) for t in new_tasks)
        print(f"{GREEN}✓ 成功添加 {len(new_tasks)} 个任务（ID：{ids}）{RESET}")


def delete_task(task_ids: List[int]):
    """删除任务并重整ID序列"""
    tasks = load_tasks()
    original_count = len(tasks)

    # 过滤要删除的任务
    remaining_tasks = [t for t in tasks if t["id"] not in task_ids]

    # 处理未找到的ID
    not_found = set(task_ids) - {t["id"] for t in tasks}
    if not_found:
        print(f"{RED}错误：找不到ID为 {', '.join(map(str, not_found))} 的任务{RESET}")

    # 重新分配连续ID
    for new_id, task in enumerate(remaining_tasks, start=1):
        task["id"] = new_id

    save_tasks(remaining_tasks)
    deleted_count = original_count - len(remaining_tasks)
    if deleted_count > 0:
        print(f"{GREEN}✓ 已删除 {deleted_count} 个任务，ID序列已重整{RESET}")


def toggle_status(task_ids: List[int], done: bool):
    """批量修改任务状态"""
    tasks = load_tasks()
    found_ids = set()

    for task in tasks:
        if task["id"] in task_ids:
            task["done"] = done
            found_ids.add(task["id"])

    not_found = set(task_ids) - found_ids
    if not_found:
        print(f"{RED}错误：找不到ID为 {', '.join(map(str, not_found))} 的任务{RESET}")

    if found_ids:
        save_tasks(tasks)
        action = "完成" if done else "未完成"
        print(f"{GREEN}✓ 已标记 {len(found_ids)} 个任务为 {action}{RESET}")


def list_tasks():
    """增强型任务列表显示"""
    tasks = load_tasks()

    if not tasks:
        print(f"{RED}当前没有待办事项{RESET}\n")
        return

    # 表格排版
    print(f"\n{GREEN}待办事项列表（共 {len(tasks)} 项）{RESET}")
    print(f"{'-' * 60}")
    print(f"{'序号':<4} | {'ID':<4} | {'状态':<8} | 任务内容")
    print(f"{'-' * 60}")

    for idx, task in enumerate(tasks, start=1):
        status = f"{GREEN}✓ 完成{RESET}" if task["done"] else f"{RED}✗ 未完成{RESET}"
        print(f"{idx:<4} | {task['id']:<4} | {status:<12} | {task['task']}")

    print(f"{'-' * 60}\n")


def main():
    """增强命令行参数处理"""
    parser = argparse.ArgumentParser(
        description=f"{GREEN}命令行待办事项管理器{RESET}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 参数配置
    parser.add_argument(
        "-a", "--add",
        nargs="+",
        help="添加多个任务（支持空格分隔）\n示例：todo.py -a '学习Python' '写报告'"
    )
    parser.add_argument(
        "-d", "--delete",
        nargs="+",
        type=int,
        help="删除指定ID的任务\n示例：todo.py -d 1 3"
    )
    parser.add_argument(
        "-c", "--complete",
        nargs="+",
        type=int,
        help="标记任务为已完成\n示例：todo.py -c 2 4"
    )
    parser.add_argument(
        "-u", "--uncomplete",
        nargs="+",
        type=int,
        help="标记任务为未完成\n示例：todo.py -u 5"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="显示任务列表"
    )

    args = parser.parse_args()

    # 参数处理流程
    try:
        if args.add:
            add_tasks(args.add)
        elif args.delete:
            delete_task(args.delete)
        elif args.complete:
            toggle_status(args.complete, True)
        elif args.uncomplete:
            toggle_status(args.uncomplete, False)
        elif args.list:
            list_tasks()
        else:
            parser.print_help()
    except Exception as e:
        print(f"{RED}操作失败：{str(e)}{RESET}")


if __name__ == "__main__":
    main()