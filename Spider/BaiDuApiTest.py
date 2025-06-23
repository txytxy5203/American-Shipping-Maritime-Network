# encoding:utf-8
import requests

# # 接口地址
# url = "https://api.map.baidu.com/geocoding/v3"
#
# # 此处填写你在控制台-应用管理-创建应用后获取的AK
# ak = "您的AK"
#
# params = {
#     "address":    "洋山",
#     "city":  "上海",
#     "output":    "json",
#     "ak":       "uR0KZw6B4EHFKHO8DIlmyx36TEwOmxSF",
#
# }
#
# response = requests.get(url=url, params=params)
# if response:
#     print(response.json())


# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-d29c61a7dbf749f790a52f0268b5a638", base_url="https://api.deepseek.com/v1")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)