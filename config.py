import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

DATA_STORAGE_PATH = os.getenv("DATA_STORAGE_PATH", "./data_storage")  # 数据存储路径
FILES_PATH = os.getenv("FILES_PATH", "./data_storage/files")  # 文件存储路径（原始文件存储）
MAPPING_PATH = os.getenv("MAPPING_PATH", "./data_storage/data.json")  # 索引持久化路径
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.1))  # 默认相似度阈值 10%
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data_storage/faiss.index")  # FAISS 索引路径
MAX_CONTEXT_LENGTH = os.getenv("MAX_CONTEXT_LENGTH", 209715200)  # 文本最大长度

# 环境配置（development, production, or default）
ENVIRONMENT = os.getenv("ENVIRONMENT", "default")

# 其他配置项可以继续添加
LOG_STORAGE_PATH = os.getenv("LOG_STORAGE_PATH", "./logs/app.log")  # 日志存储路径
ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"  # 默认启用加密

# 文件上传配置
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 最大文件上传大小 50MB
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,docx").split(",")  # 支持的文件类型
