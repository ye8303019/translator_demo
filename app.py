import os
import json
import requests
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import Optional

# 加载.env文件中的环境变量
load_dotenv()

app = FastAPI()
app.mount("/prompt", StaticFiles(directory="prompt"), name="prompt")
app.mount("/img", StaticFiles(directory="img"), name="img")

# 创建templates目录用于存放HTML模板
templates = Jinja2Templates(directory="templates")

class TranslationRequest(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt: str
    temperature: float = 0.6
    model: str = "doubao-1.5-lite-32k-250115"
    target_language: Optional[str] = None

# 语言映射
LANGUAGE_MAP = {
    "中文": "zh-CN",
    "English": "en",
    "日文": "ja",
    "韩文": "ko"
}

@app.get("/", response_class=HTMLResponse)
async def get_html_content(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate_stream(translation_request: TranslationRequest):
    # 检查是否为谷歌翻译请求
    if translation_request.model == "google_v1_translateHtml":
        return await google_translate_html(translation_request)
    
    # 常规大模型翻译请求
    ark_api_key = os.getenv("ARK_API_KEY")
    if not ark_api_key:
        return {"error": "ARK_API_KEY 未在.env文件中设置"}

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}"
    }
    
    print("system_prompt:", translation_request.system_prompt)
    print("user_prompt:", translation_request.user_prompt)  
    print("temperature:", translation_request.temperature)
    print("model:", translation_request.model)
    
    payload = {
        "model": translation_request.model,
        "messages": [
            {"role": "system", "content": translation_request.system_prompt},
            {"role": "user", "content": translation_request.user_prompt}
        ],
        "temperature": translation_request.temperature,
        "stream": True  # 开启流式输出
    }
    
    # 创建一个流式响应
    async def generate():
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        # 检查响应状态码
        if response.status_code != 200:
            error_message = f"请求失败，状态码: {response.status_code}, 响应: {response.text}"
            print(error_message)
            # 返回错误信息
            yield f"data: {json.dumps({'error': error_message})}\n\n"
            return
            
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # 去除 'data: ' 前缀
                    if line == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(line)
                        chunk = data['choices'][0]['delta'].get('content', '')
                        if chunk:
                            yield f"data: {chunk}\n\n"
                    except Exception as e:
                        print(f"解析数据出错: {e}")
                        print(f"错误的行: {line}")
                        continue

    return StreamingResponse(generate(), media_type="text/event-stream")

async def google_translate_html(translation_request: TranslationRequest):
    google_api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    google_host = os.getenv("GOOGLE_TRANSLATE_HOST")
    
    if not google_api_key or not google_host:
        return {"error": "谷歌翻译API配置未在.env文件中正确设置"}
    
    # 获取目标语言的代码
    if not translation_request.target_language:
        return {"error": "目标语言未指定"}
    
    target_lang_code = LANGUAGE_MAP.get(translation_request.target_language)
    if not target_lang_code:
        return {"error": f"未知的目标语言: {translation_request.target_language}"}
    
    # 准备待翻译的文本
    text_to_translate = translation_request.user_prompt
    
    url = f"https://{google_host}/v1/translateHtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "x-goog-api-key": google_api_key,
        "sec-ch-ua-mobile": "?0",
        "content-type": "application/json+protobuf"
    }
    
    # 准备请求体
    payload = [
        [
            [text_to_translate],
            "auto",
            target_lang_code
        ],
        "te_lib"
    ]
    
    print("Google Translate Request URL:", url)
    print("Google Translate Target Lang:", target_lang_code)
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # 检查响应状态码
        if response.status_code != 200:
            error_message = f"谷歌翻译请求失败，状态码: {response.status_code}, 响应: {response.text}"
            print(error_message)
            return {"error": error_message}
        
        # 解析谷歌翻译响应
        try:
            result = response.json()
            print("result:", result)
            # 谷歌翻译API返回的格式为 [['翻译结果'], ['源语言代码']]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list) and len(result[0]) > 0:
                translated_text = result[0][0]  # 直接取第一个元素即可
                print("Google Translate Success! Result:", translated_text)
                return {"result": translated_text}
            else:
                error_message = f"无法解析谷歌翻译结果: {result}"
                print(error_message)
                return {"error": error_message}
        except Exception as e:
            error_message = f"解析谷歌翻译结果出错: {str(e)}, 响应: {response.text}"
            print(error_message)
            return {"error": error_message}
            
    except Exception as e:
        error_message = f"谷歌翻译请求异常: {str(e)}"
        print(error_message)
        return {"error": error_message}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 