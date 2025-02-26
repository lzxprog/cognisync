import logging
from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np
import os
import jieba

from utils.faiss_utils import load_faiss_index
from utils.mapping_utils import load_mappings
from utils.sentence_model import get_model, encode_text
from utils.llm import call_llm, call_llm_query
from utils.text_processing import extract_file_content

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query")
async def query(query: str,openApiKey:str, k: int = 20):
    try:
        # 将问题直接解析为相关联得关键词
        keyword = call_llm_query(query,openApiKey)
        file_id_map, file_path_map = load_mappings()
        index = load_faiss_index()
        logger.info(f"Loaded FAISS index with {index.ntotal} vectors")
        model = get_model()

        tokenized_query = " ".join(jieba.cut(keyword))
        query_vector = encode_text(model, tokenized_query)
        logger.debug(f"Generated query vector with shape: {query_vector.shape}")

        query_array = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        distances, indices = index.search(query_array, k)  # 直接查询k个结果
        logger.debug(f"Search results: indices={indices}, distances={distances}")

        valid_docs = _filter_results(indices[0], distances[0], k, file_id_map, file_path_map)
        documents_content = _load_documents_content(valid_docs)
        # answer = call_llm(query, documents_content[:MAX_FILE_SIZE],openApiKey) if documents_content else "No relevant documents found."
        answer =  ""

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
    valid_docs = []
    for doc_id, distance in zip(indices, distances):
        if distance < 0:
            continue

        logger.debug(f"Checking doc {doc_id} with distance {distance}")
        if (md5 := file_id_map.get(int(doc_id))) and (path := file_path_map.get(md5)):
            if os.path.exists(path):
                valid_docs.append(path)
                if len(valid_docs) >= k:  # 关键优化点2：提前终止循环
                    break
            else:
                logger.warning(f"File not found: {path}")
        else:
            logger.warning(f"Invalid document ID: {doc_id}")
    return valid_docs


def _load_documents_content(file_paths: List[str]) -> List[str]:
    return [extract_file_content(path) for path in file_paths if os.path.exists(path)]