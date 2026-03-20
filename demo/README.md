# 灵医大模型 - 健康分析测试工具

这是一个用于测试百度灵医大模型健康数据分析能力的Web应用工具。

## 功能特点

- 📊 支持输入健康数据（血压、血氧、血糖、心率等）
- 📋 支持粘贴体检报告和病历
- 🧪 自动生成健康分析报告
- 🌐 美观的Web界面
- 📱 响应式设计

## 快速开始

### 1. 配置API密钥

首先，编辑 `config.py` 文件，填入你从百度灵医开放平台获取的 API Key 和 Secret Key：

```python
API_KEY = "你的API Key"
SECRET_KEY = "你的Secret Key"
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python app.py
```

### 4. 访问界面

打开浏览器，访问：`http://localhost:5000`

## 项目结构

```
demo/
├── config.py              # 配置文件（API密钥）
├── ly_api.py              # 灵医API封装
├── app.py                 # Flask Web应用
├── requirements.txt       # Python依赖
├── README.md             # 使用说明
└── templates/
    └── index.html        # Web界面
```

## 使用说明

1. 在"健康数据"文本框中输入你的健康指标，例如：
   ```
   血压：135/85 mmHg
   心率：78 次/分
   血氧：97%
   空腹血糖：6.2 mmol/L
   ```

2. （可选）在"体检报告/病历"文本框中粘贴你的体检报告或病历内容

3. 点击"开始健康分析"按钮

4. 等待灵医大模型生成健康报告

## 示例数据

界面提供了两个示例数据按钮，可以快速填充测试数据：

- **示例数据1**：健康指标基本正常的数据
- **示例数据2**：有一些健康风险的数据

## 注意事项

- ⚠️ 此工具仅供测试和学习使用，不能替代专业医疗诊断
- 🔒 请妥善保管你的API密钥，不要泄露给他人
- 📊 确保输入的数据格式清晰，便于模型理解
- ⏱️ 分析可能需要几秒钟时间，请耐心等待

## 技术栈

- Python 3.x
- Flask (Web框架)
- Requests (HTTP请求)
- HTML/CSS/JavaScript (前端)

## 获取帮助

如有问题，请参考百度灵医开放平台文档：
https://01bot.baidu.com/doc/01bot/v4/develop/chat/
