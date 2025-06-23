import os

from volcenginesdkarkruntime import Ark

# Authentication
# 1.If you authorize your endpoint using an API key, you can set your api key to environment variable "ARK_API_KEY"
# or specify api key by Ark(api_key="${YOUR_API_KEY}").
# Note: If you use an API key, this API key will not be refreshed.
# To prevent the API from expiring and failing after some time, choose an API key with no expiration date.

# 2.If you authorize your endpoint with Volcengine Identity and Access Management（IAM), set your api key to environment variable "VOLC_ACCESSKEY", "VOLC_SECRETKEY"
# or specify ak&sk by Ark(ak="${YOUR_AK}", sk="${YOUR_SK}").
# To get your ak&sk, please refer to this document(https://www.volcengine.com/docs/6291/65568)
# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）
client = Ark(api_key="${f768b4d8-e49e-4a55-a5ec-b069c00da6db}")


resp = client.chat.completions.create(
    model="doubao-1-5-pro-32k-250115",
    messages=[{"content": "天空为什么是蓝色的？", "role": "user"}],
)

# 深度思考模型，且触发了深度思考，打印思维链内容
if hasattr(resp.choices[0].message, 'reasoning_content'):
    print(resp.choices[0].message.reasoning_content)

print(resp.choices[0].message.content)