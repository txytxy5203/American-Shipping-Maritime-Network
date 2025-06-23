import requests
from bs4 import BeautifulSoup

def GET_Country_Html():
    url = "https://gangkou.gongjucha.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    Country_html = []

    try:
        # 发送 GET 请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查 HTTP 错误状态
        response.encoding = response.apparent_encoding  # 自动识别编码

        # 解析 HTML
        soup = BeautifulSoup(response.text, "lxml")

        # 示例：提取港口列表（需根据实际网页结构调整）
        port_list = soup.find_all("div", class_="panel-body")  # 假设港口信息在 class 为 port-item 的 div 中
        ppp = port_list[2].find_all("a")
        for port in ppp:
            port = port.get("href")
            Country_html.append(port)
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
    except Exception as e:
        print(f"解析失败：{e}")
    return Country_html
    # for item in Country_html:
    #     print(item)
    # print(len(Country_html))
