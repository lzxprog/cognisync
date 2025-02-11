import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Data Storage Directory
DATA_STORAGE = os.getenv("DATA_STORAGE", "./data_storage")

# Log Storage Directory
LOG_STORAGE = os.getenv("LOG_STORAGE", "./logs")

# Search Index Directory
INDEX_STORAGE = os.getenv("INDEX_STORAGE", "./search_index")
