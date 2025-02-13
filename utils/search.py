import faiss
import numpy as np
from config import SIMILARITY_THRESHOLD
from typing import List, Tuple

def search_in_faiss(query_vector: np.ndarray, index: faiss.Index, threshold=SIMILARITY_THRESHOLD, k=5) -> List[Tuple[int, float]]:
    """
    在 FAISS 索引中执行查询，并返回所有相似度大于阈值的文档。

    :param query_vector: 查询向量 (1, D) 数组，D 为向量的维度。
    :param index: FAISS 索引对象，存储文档的向量。
    :param threshold: 相关度阈值，默认通过配置文件读取。用于筛选相关度较低的文档。
    :param k: 返回的最相关文档数量。默认值为 5。

    :return: 返回符合阈值的文档（文档索引和相似度评分）
    """
    try:
        # 执行 FAISS 查询
        D, I = index.search(query_vector, k)  # D: 相似度评分, I: 文档索引

        # 筛选出所有相似度大于阈值的文档
        relevant_docs = [(i, D[0][i]) for i in range(len(D[0])) if D[0][i] >= threshold]

        return relevant_docs

    except Exception as e:
        raise Exception(f"Error during FAISS search: {str(e)}")


def load_faiss_index(index_path: str) -> faiss.Index:
    """
    加载存储在磁盘上的 FAISS 索引文件。

    :param index_path: FAISS 索引文件的路径
    :return: 返回加载的 FAISS 索引
    """
    try:
        # 从指定路径加载 FAISS 索引
        index = faiss.read_index(index_path)
        return index
    except Exception as e:
        raise Exception(f"Error loading FAISS index from {index_path}: {str(e)}")


def build_faiss_index(vectors: np.ndarray, index_path: str) -> faiss.Index:
    """
    构建并保存 FAISS 索引。

    :param vectors: 要索引的文档向量 (N, D)，N 为文档数量，D 为向量维度
    :param index_path: 索引保存的路径
    :return: 返回构建的 FAISS 索引
    """
    try:
        # 获取向量的维度
        dim = vectors.shape[1]

        # 使用 L2 距离创建 FAISS 索引
        index = faiss.IndexFlatL2(dim)

        # 将向量添加到索引中
        index.add(vectors)

        # 保存索引到磁盘
        faiss.write_index(index, index_path)

        return index
    except Exception as e:
        raise Exception(f"Error building FAISS index: {str(e)}")
