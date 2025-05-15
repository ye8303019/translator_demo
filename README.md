# ARK API 翻译器

这是一个使用Python调用ARK API的翻译应用，包括一个命令行脚本和一个网页应用界面。

## 安装依赖

```bash
pip install requests python-dotenv fastapi uvicorn jinja2
```

## 准备工作

创建`.env`文件并添加你的API密钥：

```
ARK_API_KEY=你的实际API密钥
```

## 使用方法

### 命令行脚本

运行原始的命令行脚本：

```bash
python translator_demo.py
```

### 网页应用

启动网页应用：

```bash
python app.py
```

然后在浏览器中访问 http://localhost:8000 即可使用网页版翻译器。

## 网页应用功能

1. 在"系统提示"文本框中输入系统指令
2. 在"用户提示"文本框中输入要翻译的内容
3. 点击"翻译"按钮
4. 翻译结果会实时流式显示在下方结果区域

## 脚本说明

- `translator_demo.py`: 命令行脚本，发送固定请求到ARK API
- `app.py`: Web应用后端，处理前端请求并与ARK API通信
- `templates/index.html`: 前端页面，提供用户交互界面 