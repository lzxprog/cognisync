import logging
from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np
import os
import jieba  # 引入jieba库进行中文分词

from config import MAX_FILE_SIZE
from utils.faiss_utils import load_faiss_index
from utils.mapping_utils import load_mappings
from utils.sentence_model import get_model, encode_text
from utils.llm import call_llm
from utils.text_processing import extract_file_content

# 获取日志记录器
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query")
async def query(query: str, k: int = 2):
    try:
        # 实时加载最新资源
        file_id_map, file_path_map = load_mappings()
        index = load_faiss_index()
        logger.info(f"Loaded FAISS index with {index.ntotal} vectors")  # Debug log for index load
        model = get_model()

        # 中文查询文本分词
        tokenized_query = " ".join(jieba.cut(query))  # 使用jieba进行分词

        # 编码查询（注意，传入的是分词后的查询文本）
        query_vector = encode_text(model, tokenized_query)
        logger.info(f"Generated query vector with shape: {query_vector.shape}")  # Debug log for query vector

        # 将查询向量转换为二维数组
        query_array = np.array(query_vector, dtype=np.float32).reshape(1, -1)

        # 相似性搜索
        distances, indices = index.search(query_array, len(file_id_map.keys()))
        logger.info(f"Search results: indices={indices}, distances={distances}")  # Debug log for search results

        # 结果过滤
        valid_docs = _filter_results(indices[0], distances[0], k, file_id_map, file_path_map)

        # 获取文档内容
        documents_content = _load_documents_content(valid_docs)

        # 确保正确切片列表
        if documents_content:
            # answer = call_llm(query, documents_content[:MAX_FILE_SIZE])
            answer = '文档'
        else:
            answer = "No relevant documents found."

        return {
            "answer": answer,
            "relevant_documents": valid_docs,
            "distances": distances[0].tolist()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def _filter_results(indices, distances, k, file_id_map, file_path_map) -> List[str]:
    """返回最相似的k个文件"""
    valid_docs = []

    # 将文档ID和距离一起打包并按距离升序排序
    sorted_results = sorted(zip(indices, distances), key=lambda x: x[1])

    # 获取最相似的k个文档
    for doc_id, distance in sorted_results[:k]:  # 只取前k个最小距离的文档
        logger.info(f"Checking doc {doc_id} with distance {distance}")  # Debug log for filtering
        if distance < 0:  # 确保距离为正数
            continue

        # 获取文档的路径
        if (md5 := file_id_map.get(int(doc_id))) and (path := file_path_map.get(md5)):
            if os.path.exists(path):
                valid_docs.append(path)
            else:
                logger.warning(f"File not found: {path}")
        else:
            logger.warning(f"Invalid document ID: {doc_id}")

    return valid_docs

def _load_documents_content(file_paths: List[str]) -> List[str]:
    """安全加载文档内容"""
    content = []
    for path in file_paths:
        try:
            content.append(extract_file_content(path))
        except Exception as e:
            logger.error(f"Error reading {path}: {str(e)}")
    return content  # Return a list of document content, not a single string
