# Cognisync - AI Data Bridge

Cognisync is an AI-powered data asset bridge that enables seamless interaction between enterprise data and AI models. This system ensures secure encrypted storage, intelligent data processing, AI-driven queries, and irreversible secure data destruction.

## 🚀 Features
- **Secure Data Upload**: Automatically encrypts files using AES-256-GCM and binds them to a unique device ID.
- **AI-Powered Querying**: Enables intelligent queries with LLM models (GPT-4, Claude, Llama2) while maintaining security.
- **Intelligent Data Preprocessing**: Extracts, cleans, and structures data from various formats (PDF, Word, JSON, logs, etc.).
- **Traceable AI Responses**: Logs referenced documents for each AI-generated response, ensuring transparency.
- **Secure Data Destruction**: Implements multi-pass overwriting and hardware-specific TRIM operations to prevent data recovery.

## 📁 Project Structure
```
Cognisync/
│── main.py                # FastAPI entry point
│── config.py              # Configuration file
│── requirements.txt       # Dependency list
│── .env                   # API keys and environment variables
│
├── routes/                # API endpoints
│   ├── upload.py          # Handles file uploads
│   ├── query.py           # AI querying
│   ├── destroy.py         # Secure deletion
│
├── utils/                 # Utility modules
│   ├── encryption.py      # AES encryption & device binding
│   ├── text_processing.py # Text extraction & preprocessing
│   ├── search.py          # Search & AI processing
│   ├── secure_delete.py   # Secure wiping
│
├── data_storage/          # Encrypted data storage
│
├── logs/                  # AI query logs
│
└── README.md              # Project documentation
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

### 3️⃣ Configure environment variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY="sk-xxx"
DATA_STORAGE="./data_storage"
LOG_STORAGE="./logs"
```

### 4️⃣ Run the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📌 API Endpoints
| Method   | Endpoint             | Description |
|----------|----------------------|-------------|
| `POST`   | `/upload`            | Uploads and encrypts a file |
| `POST`   | `/query`             | AI-powered query on encrypted data |
| `GET`    | `/logs/{query_id}`   | Retrieves AI response references |
| `DELETE` | `/destroy/{file_id}` | Securely destroys a file |

## 🔥 Next Steps
✅ Implement `/upload` API for secure file handling
✅ Integrate AES encryption & device binding
🔜 Develop `/query` API for AI-powered data search
🔜 Implement `/destroy` API for secure deletion

---
### 🚀 Cognisync: Bridging AI & Enterprise Data Securely
