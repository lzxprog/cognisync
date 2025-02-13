from fastapi import APIRouter, HTTPException
from routes.upload import file_id_map, file_path_map  # 从 upload.py 导入映射
from utils.llm import call_llm  # 引入 LLM 调用函数
from config import FAISS_INDEX_PATH
import faiss
import numpy as np
import logging

from utils.sentence_model import get_model, encode_text

# 创建查询路由
router = APIRouter()

# 加载 FAISS 索引
def load_faiss_index_from_disk() -> faiss.Index:
    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
        return index
    except Exception as e:
        logging.error(f"Error loading FAISS index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading FAISS index: {str(e)}")

# 读取文件内容并转化为文本（假设是文本文件）
def read_file_content(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return ""

# 查询接口
@router.post("/query")
async def query(query: str, k: int = 3):
    try:
        # 加载 FAISS 索引
        faiss_index = load_faiss_index_from_disk()

        # 获取 Sentence-BERT 模型
        model = get_model()

        # 将查询转化为向量
        query_vector = np.array(encode_text(model, query), dtype=np.float32)

        # 使用 FAISS 进行检索
        D, I = faiss_index.search(query_vector.reshape(1, -1), k)  # FAISS 要求输入是二维数组

        # 获取相关文档路径
        relevant_docs = []
        for i in range(k):
            doc_id = I[0][i]
            # 获取文件的 MD5
            file_md5 = file_id_map.get(doc_id)
            if file_md5:
                # 使用 MD5 获取文件路径
                file_path = file_path_map.get(file_md5)
                if file_path:
                    relevant_docs.append(file_path)
                else:
                    logging.warning(f"No file path found for MD5 {file_md5}")
            else:
                logging.warning(f"No file ID found for FAISS ID {doc_id}")

        if not relevant_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found.")

        # 读取所有相关文件的内容并合并
        documents_content = ""
        for file_path in relevant_docs:
            file_content = read_file_content(file_path)
            documents_content += file_content + "\n"  # 合并文件内容

        # 调用 LLM 生成答案
        answer = call_llm(query, documents_content)

        return {"answer": answer, "relevant_documents": relevant_docs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")