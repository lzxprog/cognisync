<div align="center">
  <img src="./logo.png" width="30%" alt="cognisync" />
</div>
<hr>

# cognisync - AI Data Bridge!

cognisync is an AI-powered data asset bridge that enables seamless interaction between enterprise data and AI models. This system ensures secure encrypted storage, intelligent data processing, AI-driven queries, and irreversible secure data destruction.

## 🚀 Features
- **Secure Data Upload**: Automatically encrypts files using AES-256-GCM and binds them to a unique device ID.
- **AI-Powered Querying**: Enables intelligent queries with LLM models (GPT-4, Claude, Llama2) while maintaining security.
- **Intelligent Data Preprocessing**: Extracts, cleans, and structures data from various formats (PDF, Word, JSON, logs, etc.).
- **Traceable AI Responses**: Logs referenced documents for each AI-generated response, ensuring transparency.
- **Secure Data Destruction**: Implements multi-pass overwriting and hardware-specific TRIM operations to prevent data recovery.

## 📁 Project Structure
```
cognisync/
cognisync/
│── main.py                # FastAPI 主入口文件，启动应用并注册路由
│── config.py              # 配置文件，包含文件路径、FAISS 索引路径等设置
│── requirements.txt       # 依赖库清单文件
│── .env                   # 环境变量（如 OpenAI API 密钥等）

├── routes/                # API 路由
│   ├── upload.py          # 处理文件上传并生成文档摘要和分类
│   ├── query.py           # 处理用户查询，返回基于文档的答案
│
├── utils/                 # 工具类和模块
│   ├── llm.py             # 与 GPT-3 或 T5 进行交互，生成答案
│   ├── text_processing.py # 文本提取和处理工具（如 docx 文件内容提取）
│   ├── search.py          # FAISS 索引和查询相关文档的工具
│
├── data_storage/          # 存储上传文件和 FAISS 索引
│   ├── files/             # 保存上传的文档文件
│   ├── faiss_index/       # 存储 FAISS 索引文件
│
└── README.md              # 项目说明文档
```

## 🔧 Installation
### 1️⃣ Setup virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📌 API Endpoints
| Method   | Endpoint             | Description |
|----------|----------------------|-------------|
| `POST`   | `/query`             | AI-powered query on encrypted data |

## 🔥 Next Steps
🔜 Develop `/query` API for AI-powered data search
---
### 🚀 cognisync: Bridging AI & Enterprise Data Securely
