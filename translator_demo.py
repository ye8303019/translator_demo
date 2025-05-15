import os
import json
import requests
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量中获取API密钥
ark_api_key = os.getenv("ARK_API_KEY")
if not ark_api_key:
    raise ValueError("ARK_API_KEY 未在.env文件中设置")

# API请求URL
url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ark_api_key}"
}

# 请求体
payload = {
    "model": "ep-20250514183820-ct5ks",
    "messages": [
        {"role": "system", "content": "你是人工智能助手."},
        {"role": "user", "content": "常见的十字花科植物有哪些？"}
    ]
}

# 发送请求
response = requests.post(url, headers=headers, json=payload)

# 打印响应结果
if response.status_code == 200:
    print("请求成功！")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text) 