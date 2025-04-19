import requests
from lxml import etree
import mysql.connector
import datetime


def download(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text


def spider(html_str):
    html = etree.HTML(html_str)

    # 提取城市
    city = html.xpath("//dd[@class='name']/h1/text()")[0].replace('天气', '').strip()

    # 提取日期
    date_str = html.xpath("//dd[@class='week']/text()")[0].strip().split('　')[0]

    # 提取所有小时数据块
    time_blocks = html.xpath("//div[contains(@class, 'day7')]")

    weather_data = []

    for block_idx, block in enumerate(time_blocks, 1):
        # 时间点
        times = block.xpath(".//ul[@class='txt canvas_hour']/li/text()")
        # 天气情况
        weathers = block.xpath(".//ul[@class='txt txt2']/li/text()")
        # 风向
        wind_directions = block.xpath(".//ul[@class='txt'][1]/li/text()")
        # 风力等级
        wind_levels = block.xpath(".//ul[@class='txt'][2]/li/text()")
        # 温度
        temps = block.xpath(f".//div[@class='zxt_shuju{block_idx}']/ul/li/span/text()")

        # 组合每个小时的数据
        for i in range(len(times)):
            time = times[i].strip()
            weather = weathers[i].strip()
            wind = f"{wind_directions[i].strip()}{wind_levels[i].strip()}"
            temp = temps[i].strip()

            weather_data.append({
                'city': city,
                'date': date_str,
                'time': time,
                'weather': weather,
                'wind': wind,
                'temperature': temp
            })

    return weather_data


def data_writer(items):
    # 数据库配置（需根据实际情况修改）
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='@TT12345yy..',
        database='test'
    )
    cursor = conn.cursor()

    # 创建表（确保表结构正确，这里使用已有表结构）
    # 注意：实际使用时建议检查表是否存在，避免重复创建
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS weather
                   (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       city VARCHAR(50),
                       date DATE,
                       time VARCHAR(10),
                       weather VARCHAR(50),
                       wind VARCHAR(50),
                       temperature INT
                       )
                   ''')

    # 插入数据
    for item in items:
        date_obj = datetime.datetime.strptime(item['date'], '%Y年%m月%d日').date()
        cursor.execute('''
                       INSERT INTO weather (city, date, time, weather, wind, temperature)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ''', (
            item['city'],
            date_obj,
            item['time'],
            item['weather'],
            item['wind'],
            int(item['temperature'])
                       ))

    conn.commit()
    cursor.close()
    conn.close()


def main():
    # 新增城市列表（城市名: 拼音路径）
    cities = {
        '武汉': 'wuhan',
        '上海': 'shanghai',
        '广州': 'guangzhou',
        '天津': 'tianjin',
        '北京': 'beijing',
        '南京': 'nanjing',
        '重庆': 'chongqing',
        '杭州': 'hangzhou'
    }

    for city_name, city_path in cities.items():
        url = f'https://www.tianqi.com/{city_path}/'
        html_content = download(url)
        weather_items = spider(html_content)
        data_writer(weather_items)
        print(f"{city_name} 天气数据爬取完成")


if __name__ == '__main__':
    main()