from fastapi import APIRouter, HTTPException
from utils.llm import call_llm  # 改为 call_llm 来支持更多模型
from utils.search import search_in_faiss, load_faiss_index
from utils.sentence_model import get_model, encode_text  # 从 sentence_model 中导入相关功能
from utils.text_processing import extract_text_from_pdf, extract_text_from_docx  # 支持多格式文件
from config import SIMILARITY_THRESHOLD, FAISS_INDEX_PATH, FILES_PATH
import numpy as np
import faiss
from typing import List

router = APIRouter()

# 获取已加载的模型
model = get_model()

# 加载 FAISS 索引
def load_faiss_index_from_disk() -> faiss.Index:
    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
        return index
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading FAISS index: {str(e)}")

# 获取相关文档内容
def get_relevant_documents(index: faiss.Index, query: str, k: int = 3) -> List[str]:
    try:
        # 将查询转化为向量
        query_vector = encode_text(model, query)

        # 使用 FAISS 进行检索
        D, I = index.search(np.array([query_vector], dtype='float32'), k)

        # 筛选相关文档
        relevant_docs = []
        for i, dist in zip(I[0], D[0]):
            if dist < SIMILARITY_THRESHOLD:
                break
            # 提取文档内容
            doc_path = f"{FILES_PATH}/document_{i}.pdf"  # 根据索引获取文档路径
            relevant_doc_content = extract_text_from_pdf(doc_path) if doc_path.endswith(".pdf") else extract_text_from_docx(doc_path)
            relevant_docs.append(relevant_doc_content)

        return relevant_docs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving relevant documents: {str(e)}")

# 查询处理接口
@router.post("/query")
async def query(query: str, k: int = 3):
    try:
        # 加载 FAISS 索引
        faiss_index = load_faiss_index_from_disk()

        # 获取相关文档
        relevant_docs = get_relevant_documents(faiss_index, query, k)

        if not relevant_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found.")

        # 使用 LLM 生成答案
        answer = call_llm(query, " ".join(relevant_docs))

        return {"answer": answer, "relevant_documents": relevant_docs}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")