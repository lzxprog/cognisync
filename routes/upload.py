from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import os
import faiss
import numpy as np
from utils.sentence_model import get_model, encode_text  # 从 sentence_model 中导入相关功能
from utils.text_processing import extract_text_from_pdf, extract_text_from_docx  # 支持提取 PDF 和 DOCX 文件文本
from config import FILES_PATH, FAISS_INDEX_PATH
from typing import List

router = APIRouter()

# 获取已加载的模型
model = get_model()

# 确保文件存储目录存在
Path(FILES_PATH).mkdir(parents=True, exist_ok=True)

# 初始化 FAISS 索引
index = faiss.IndexFlatL2(384)  # 384是模型输出的向量维度

# 将 FAISS 索引保存到文件
def save_faiss_index(index: faiss.Index, index_path: str):
    try:
        faiss.write_index(index, index_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving FAISS index: {str(e)}")

# 加载 FAISS 索引
def load_faiss_index(index_path: str) -> faiss.Index:
    try:
        return faiss.read_index(index_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading FAISS index: {str(e)}")

# 上传文件并处理
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 获取文件保存路径
        file_path = os.path.join(FILES_PATH, file.filename)

        # 保存文件到本地
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 提取文件内容
        file_content = ""
        if file.filename.endswith(".pdf"):
            file_content = extract_text_from_pdf(file_path)
        elif file.filename.endswith(".docx"):
            file_content = extract_text_from_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and DOCX are supported.")

        # 使用 Sentence-BERT 生成文档向量
        doc_vector = encode_text(model, file_content)

        # 将文档向量添加到 FAISS 索引
        index.add(np.array([doc_vector], dtype='float32'))

        # 保存 FAISS 索引
        save_faiss_index(index, FAISS_INDEX_PATH)

        return {"message": "File uploaded and processed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
