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

# 加载.env文件中的环境变量
load_dotenv()

app = FastAPI()
app.mount("/prompt", StaticFiles(directory="prompt"), name="prompt")
app.mount("/img", StaticFiles(directory="img"), name="img")

# 创建templates目录用于存放HTML模板
templates = Jinja2Templates(directory="templates")

class TranslationRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    temperature: float = 0.6
    model: str = "doubao-lite-32k-240828"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate_stream(translation_request: TranslationRequest):
    ark_api_key = os.getenv("ARK_API_KEY")
    if not ark_api_key:
        return {"error": "ARK_API_KEY 未在.env文件中设置"}

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}"
    }
    
    print("system_prompt:",translation_request.system_prompt)
    print("user_prompt:",translation_request.user_prompt)  
    print("temperature:",translation_request.temperature)
    print("model:",translation_request.model)
    
    payload = {
        "model": translation_request.model,
        "messages": [
            {"role": "system", "content": translation_request.system_prompt},
            {"role": "user", "content": translation_request.user_prompt}
        ],
        "temperature": translation_request.temperature,
        "stream": True  # 开启流式输出
    }

    def generate():
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        if response.status_code != 200:
            yield f"data: {{\"error\": \"请求失败，状态码: {response.status_code}\"}}\n\n"
            return

        for line in response.iter_lines():
            if line:
                # 移除 "data: " 前缀并解析JSON
                try:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_json = line_text[6:]  # 移除 "data: " 前缀
                        if line_json == "[DONE]":
                            break
                        data = json.loads(line_json)
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                except Exception as e:
                    yield f"data: {{\"error\": \"处理响应时出错: {str(e)}\"}}\n\n"
                    break

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 