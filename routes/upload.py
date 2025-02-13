import os
import hashlib
from pathlib import Path
import faiss
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
from config import FILES_PATH, FAISS_INDEX_PATH
import logging
from utils.sentence_model import get_model, encode_text  # 引入模型加载和编码方法

# 初始化上传路由
router = APIRouter()

# 文件路径存储目录，确保该目录存在
Path(FILES_PATH).mkdir(parents=True, exist_ok=True)

# 用于存储文件 MD5 与faiss的映射
file_id_map = {}

# 用于存储文件 MD5 与文件路径的映射
file_path_map = {}

# 加载或创建 FAISS 索引
def load_or_create_faiss_index() -> faiss.Index:
    try:
        # 如果 FAISS 索引文件存在，加载它
        if Path(FAISS_INDEX_PATH).exists():
            return faiss.read_index(FAISS_INDEX_PATH)
        else:
            # 如果索引文件不存在，创建一个新的 FAISS 索引
            dimension = 384  # 向量的维度，这里需要根据实际情况调整
            index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离度量
            return index
    except Exception as e:
        logging.error(f"Error loading or creating FAISS index: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading or creating FAISS index")


# 计算文件的 MD5 值
def calculate_md5(file: UploadFile) -> str:
    hash_md5 = hashlib.md5()
    for chunk in file.file:
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


# 读取文件内容并转化为文本（假设是文本文件）
async def read_file_content(file: UploadFile) -> str:
    content = await file.read()
    return content.decode("utf-8")  # 假设文件内容为 UTF-8 编码的文本


# 上传文件并更新映射
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 计算文件的 MD5 值
        file_md5 = calculate_md5(file)

        # 如果文件的 MD5 值已经在 map 中，则认为文件已上传
        if file_md5 in file_id_map:
            return {"message": "File already uploaded", "file_md5": file_md5}

        # 获取文件保存路径
        file_path = os.path.join(FILES_PATH, file.filename)

        # 保存文件路径到 map 中
        file_path_map[file_md5] = file_path

        # 保存文件到本地
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 加载或创建 FAISS 索引
        faiss_index = load_or_create_faiss_index()

        # 获取 Sentence-BERT 模型
        model = get_model()

        # 读取文件内容并生成文本向量
        file_content = await read_file_content(file)
        file_vector = np.array(encode_text(model, file_content), dtype=np.float32)  # 获取文件向量

        # 将文件向量添加到 FAISS 索引
        faiss_index.add(file_vector.reshape(1, -1))  # FAISS 需要二维数组作为输入

        # 获取新增文档的 ID
        doc_id = faiss_index.ntotal - 1

        # 更新 file_id_map
        file_id_map[doc_id] = file_md5  # 使用 FAISS ID 作为键
        logging.info(f"File {file.filename} uploaded with MD5 {file_md5} and associated with FAISS ID {doc_id}")

        # 保存更新后的 FAISS 索引
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)

        return {"filename": file.filename, "file_md5": file_md5, "faiss_id": doc_id}

    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
