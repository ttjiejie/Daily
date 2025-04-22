import requests
import json

from dotenv import load_dotenv
import os

# 颜色常量
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

# 加载.env文件中的环境变量
load_dotenv()
API_KEY = os.getenv('API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city_name, proxy=None):
    """
    获取指定城市的天气信息
    :param city_name: 城市名称
    :param proxy: 代理设置，格式为{"http": "http://proxy:port", "https": "http://proxy:port"}
    :return: 天气信息字典
    """
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',  # 使用摄氏度
        'lang': 'zh_cn'  # 中文结果
    }
    for attempt in range(max_retries):
        try:
            proxies = proxy if proxy else {}
            response = requests.get(BASE_URL, params=params, proxies=proxies, timeout=15)  # 添加15秒超时
            response.raise_for_status()  # 检查请求是否成功

            weather_data = response.json()

            # 提取关键天气信息
            result = {
                'city': weather_data['name'],
                'temperature': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'humidity': weather_data['main']['humidity'],
                'weather': weather_data['weather'][0]['description'],
                'wind_speed': weather_data['wind']['speed']
            }

            return result

        except requests.exceptions.Timeout:
            print(f"{RED}超时，正在重试 ({attempt + 1}/{max_retries}){RESET}")
            if attempt == max_retries - 1:
                print(f"{RED}错误：超过最大重试次数{RESET}")
                return None

        except requests.exceptions.Timeout:
            print(f"{RED}错误：请求超时，请检查网络连接{RESET}")
            print(f"{RED}提示：可能是网络问题或API服务器响应慢，请稍后重试{RESET}")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"{RED}错误：API请求失败，状态码：{e.response.status_code}{RESET}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"{RED}错误：请求天气API时出错: {e}{RESET}")
            return None

def batch_query(cities, proxy=None):
    """
    批量查询多个城市的天气
    :param cities: 城市名称列表
    :return: 天气信息字典列表
    """
    results = []
    for city in cities:
        weather = get_weather(city, proxy=proxy)
        if weather:
            results.append(weather)
    return results

def save_to_csv(weather_data, filename='weather_history.csv'):
    """
    将天气数据保存到CSV文件
    :param weather_data: 天气数据字典或字典列表
    :param filename: 保存的文件名
    """
    import csv
    from datetime import datetime
    
    if not isinstance(weather_data, list):
        weather_data = [weather_data]
    
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:  # 如果是新文件，写入表头
            writer.writerow(['城市', '温度(°C)', '体感温度(°C)', '湿度(%)', '天气状况', '风速(m/s)', '查询时间'])
        
        for data in weather_data:
            writer.writerow([
                data['city'],
                data['temperature'],
                data['feels_like'],
                data['humidity'],
                data['weather'],
                data['wind_speed'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])

if __name__ == "__main__":
    print("1. 单城市查询\n2. 多城市批量查询")
    choice = input("请选择查询模式(1/2): ")
    
    if choice == '1':
        use_proxy = input("是否使用代理？(y/n): ").lower()
        proxy = {"http": "http://10.10.1.10:3128"} if use_proxy == 'y' else None
        city = input("请输入要查询的城市名称: ")
        weather = get_weather(city, proxy=proxy)

        if weather:
            print(f"\n城市: {weather['city']}")
            print(f"温度: {weather['temperature']}°C")
            print(f"体感温度: {weather['feels_like']}°C")
            print(f"湿度: {weather['humidity']}%")
            print(f"天气状况: {weather['weather']}")
            print(f"风速: {weather['wind_speed']} m/s")
            save_to_csv(weather)
        else:
            print("无法获取天气信息，请检查城市名称或API密钥。")
    elif choice == '2':
        cities = input("请输入要查询的城市名称(多个城市用逗号分隔): ").split(',')
        cities = [city.strip() for city in cities if city.strip()]
        proxy = {"http": "http://10.10.1.10:3128"}
        weather_list = batch_query(cities, proxy=proxy)

        if weather_list:
            for weather in weather_list:
                print(f"\n城市: {weather['city']}")
                print(f"温度: {weather['temperature']}°C")
                print(f"体感温度: {weather['feels_like']}°C")
                print(f"湿度: {weather['humidity']}%")
                print(f"天气状况: {weather['weather']}")
                print(f"风速: {weather['wind_speed']} m/s")
            save_to_csv(weather_list)
        else:
            print("无法获取任何城市的天气信息，请检查城市名称或API密钥。")