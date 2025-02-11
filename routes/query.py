import logging

from fastapi import APIRouter, HTTPException
from utils.encryption import decrypt_data, get_device_id
from utils.search import search_related_files
from config import DATA_STORAGE
from utils.llm import call_llm

router = APIRouter()

# ✅ 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def query_data(question: str):
    try:
        logging.info("Received query: %s", question)
        # 搜索与问题相关的加密文件
        relevant_files = search_related_files(question, DATA_STORAGE)
        if not relevant_files:
            raise HTTPException(status_code=404, detail="No relevant data found")

        # 设备密钥
        device_key = get_device_id()

        # 解密相关文件
        decrypted_texts = []
        for file_path in relevant_files:
            with open(file_path, "r") as f:
                encrypted_content = f.read()
            decrypted_texts.append(decrypt_data(encrypted_content, device_key))

        # 传递数据给 LLM 生成答案
        response = call_llm(question, decrypted_texts)

        return {"question": question, "answer": response, "sources": relevant_files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
