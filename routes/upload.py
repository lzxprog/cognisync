import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import docx
import jieba
from utils.encryption import encrypt_data, get_device_id
from config import DATA_STORAGE

# ✅ 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 定义本地知识库文件
KNOWLEDGE_BASE_FILE = os.path.join(DATA_STORAGE, "knowledge_base.enc")


def extract_text_from_docx(file_bytes):
    """从 DOCX 文件提取所有文本内容"""
    try:
        with open("temp.docx", "wb") as temp_file:
            temp_file.write(file_bytes)
        doc = docx.Document("temp.docx")
        os.remove("temp.docx")  # 删除临时文件
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from DOCX: {str(e)}")


def tokenize_text(text):
    """对文本进行分词"""
    return " ".join(jieba.cut(text))


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 读取文件内容（保持二进制）
        file_bytes = await file.read()

        # 解析 DOCX 文件文本
        file_text = extract_text_from_docx(file_bytes)

        logger.info("1")
        # 生成设备密钥
        device_key = get_device_id()
        logger.info("2")
        # 进行分词处理
        tokenized_text = tokenize_text(file_text)
        logger.info("3")

        # 加载现有的知识库
        if os.path.exists(KNOWLEDGE_BASE_FILE):
            with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
                existing_data = f.read()
        else:
            existing_data = ""

        # 追加新数据
        updated_data = existing_data + "\n" + tokenized_text

        # 加密并存储知识库
        encrypted_data = encrypt_data(updated_data, device_key)
        with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted_data)

        logger.info("4 - Knowledge base updated.")

        return {"message": "File uploaded, processed, and added to knowledge base", "file": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")