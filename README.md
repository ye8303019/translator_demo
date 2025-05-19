# ARK API & Google 翻译工具

这是一个多功能翻译工具，支持通过ARK大模型API和Google翻译API进行文本翻译。提供了友好的Web界面，支持流式输出翻译结果。

## 功能特点

- 支持ARK大模型API进行AI翻译
- 支持Google翻译API进行传统翻译
- 支持中文、英文、日文、韩文等多种语言
- 提供流式输出，实时查看翻译进度
- 可调节温度参数，控制翻译的创造性
- 内置多种翻译提示词模板

## 安装依赖

使用pip安装所需的依赖包：

```bash
pip install -r requirements.txt
```

## 环境配置

创建`.env`文件（参考env.example）并添加你的API密钥：

```
ARK_API_KEY=你的ARK API密钥
GOOGLE_TRANSLATE_API_KEY=你的Google翻译API密钥
GOOGLE_TRANSLATE_HOST=translate-pa.googleapis.com
```

## 使用方法

启动Web应用：

```bash
python app.py
```

然后在浏览器中访问 http://localhost:8000 即可使用翻译工具。

## Web应用使用说明

1. 选择翻译模型（ARK模型或Google翻译）
2. 选择目标语言（中文、英文、日文、韩文等）
3. 对于ARK模型翻译：
   - 可以选择预设的系统提示词或自定义
   - 可以调节温度参数
4. 在输入框中输入要翻译的文本
5. 点击"翻译"按钮
6. 翻译结果会实时流式显示在下方结果区域

## 项目结构

- `app.py`: Web应用后端，处理前端请求并与翻译API通信
- `templates/index.html`: 前端页面，提供用户交互界面
- `prompt/`: 包含不同语言的翻译提示词模板
- `img/`: 存放界面所需的图片资源
- `requirements.txt`: 项目依赖包列表

## 开发者说明

- 使用FastAPI作为后端框架
- 支持热重载，便于开发调试
- 使用Jinja2模板引擎渲染前端页面
- 通过事件流(SSE)实现翻译结果的流式输出 