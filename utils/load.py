import hashlib
import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, Optional
import jieba
import faiss
import numpy as np
import portalocker
import unicodedata

from utils.faiss_utils import load_faiss_index, save_faiss_index
from config import FILES_PATH, MAPPING_PATH
from utils.sentence_model import get_model, encode_text
from utils.text_processing import extract_file_content

# 获取日志记录器
logger = logging.getLogger(__name__)

# 初始化目录
Path(FILES_PATH).mkdir(parents=True, exist_ok=True)


def calculate_md5_from_text(text: str,
                            normalization_form: str = 'NFC',
                            strip_whitespace: bool = True,
                            chunk_size: int = 4096) -> Optional[str]:
    """
    增强版文本MD5计算函数

    参数：
    - text: 输入文本
    - normalization_form: Unicode标准化形式 (可选：NFC, NFD, NFKC, NFKD)
    - strip_whitespace: 是否移除首尾空白字符
    - chunk_size: 流式处理块大小（字节）

    返回：
    - MD5哈希字符串（小写），或 None（输入无效时）
    """
    try:
        # 输入验证
        if not isinstance(text, str):
            raise TypeError(f"Expected string, got {type(text).__name__}")

        # 文本标准化处理
        processed_text = unicodedata.normalize(normalization_form, text)

        # 空白处理
        if strip_whitespace:
            processed_text = processed_text.strip()

        # 空内容检查
        if not processed_text:
            raise ValueError("Normalized text is empty after processing")

        # 流式处理大文本
        md5_hash = hashlib.md5()
        buffer = processed_text.encode('utf-8')

        for i in range(0, len(buffer), chunk_size):
            chunk = buffer[i:i + chunk_size]
            md5_hash.update(chunk)

        return md5_hash.hexdigest().lower()

    except (TypeError, ValueError) as e:
        logger.warning(f"MD5 calculation skipped: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected MD5 calculation error: {str(e)}", exc_info=True)
        return None


class FileIndexState:
    """管理索引状态的单例类"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """初始化或加载持久化状态"""
        self.file_id_map: Dict[int, str] = {}
        self.file_path_map: Dict[str, str] = {}
        self.faiss_index: Optional[faiss.Index] = None
        self.load_mappings()

    def load_mappings(self):
        """加载映射关系"""
        try:
            logger.debug(f"Attempting to load mappings from: {MAPPING_PATH}")

            # 检查文件是否存在
            if Path(MAPPING_PATH).exists():
                # 检查文件读取权限
                if not os.access(MAPPING_PATH, os.R_OK):
                    logger.error(f"File {MAPPING_PATH} is not readable due to permission issues.")
                    raise PermissionError(f"File {MAPPING_PATH} is not readable due to permission issues.")

                try:
                    # 读取文件内容作为字符串
                    with open(MAPPING_PATH, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # 输出内容以检查文件格式
                    logger.debug(f"File content: {content}")

                    # 尝试解析 JSON
                    data = json.loads(content)

                    # 解析文件内容
                    self.file_id_map = {int(k): v for k, v in data['file_id_map'].items()}
                    self.file_path_map = data['file_path_map']

                    logger.info("Mappings loaded successfully")

                except json.JSONDecodeError as json_error:
                    logger.error(f"Failed to decode JSON from {MAPPING_PATH}: {json_error}")
                    self._create_new_mappings()
                except Exception as e:
                    logger.error(f"Failed to load mappings: {str(e)}")
                    self._create_new_mappings()
            else:
                self._create_new_mappings()

        except portalocker.LockException as lock_error:
            logger.error(f"Failed to acquire lock for {MAPPING_PATH}: {lock_error}")
            raise lock_error

    def _create_new_mappings(self):
        """创建新的映射文件"""
        self.file_id_map = {}
        self.file_path_map = {}
        self.save_mappings()
        logger.info("New mappings created")

    def save_mappings(self):
        """保存当前状态到磁盘"""
        try:
            with portalocker.Lock(MAPPING_PATH, mode='w', timeout=5) as f:
                json.dump({
                    'file_id_map': self.file_id_map,
                    'file_path_map': self.file_path_map
                }, f, indent=2)
            logger.info("Mappings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save mappings: {str(e)}")


def process_local_file(state, file_path: str) -> dict:
    filename = os.path.basename(file_path)

    try:
        # 文本提取与验证
        content = extract_file_content(file_path)
        logger.info(f"Extracted content from {content}")
        if not content:
            return {"status": "skipped", "reason": "empty_content", "file": filename}

        # MD5计算与重复检查
        file_md5 = calculate_md5_from_text(content)
        logger.info(f"Calculated MD5: {file_md5}")
        if file_md5 in state.file_path_map:
            logger.info(f"File exists: {filename} (MD5: {file_md5})")
            return {"status": "exists", "md5": file_md5, "file": filename}

        # 处理长文本
        chunks = chunk_text(content)  # 长文本拆分成多个块
        embeddings = []

        # 为每个文本块生成嵌入
        for chunk in chunks:
            vector = _encode_file_content(chunk)  # 处理每个文本块
            embeddings.append(vector)

        # 聚合多个块的嵌入
        aggregated_vector = aggregate_embeddings(embeddings)

        # 索引更新
        doc_id = _update_index(state, aggregated_vector, file_md5, file_path)

        return {"status": "success", "md5": file_md5, "id": doc_id, "file": filename}

    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
        return {"status": "error", "reason": str(e), "file": filename}


def _encode_file_content(content: str) -> np.ndarray:
    """编码文本内容并进行 L2 归一化"""
    model = get_model()

    # 对中文文本进行分词
    tokenized_text = " ".join(jieba.cut(content))  # 使用jieba分词

    # 将分词后的文本输入模型进行嵌入
    vector = encode_text(model, tokenized_text)
    vector = np.array(vector, dtype=np.float32).reshape(1, -1)  # 确保返回的是二维数组
    vector = vector / np.linalg.norm(vector, axis=1, keepdims=True)  # L2 normalization
    return vector


def chunk_text(text: str, max_tokens: int = 128) -> list:
    """滑动窗口分块函数 (改进版)

    参数：
    - text: 输入文本
    - max_tokens: 窗口大小（每个块的token数量）

    返回：
    - 包含文本块的列表，相邻块有50%重叠

    示例：
    输入: "a b c d e f g", max_tokens=4
    输出: ["a b c d", "c d e f", "e f g"]
    """
    tokens = text.split()
    chunks = []
    total_tokens = len(tokens)

    # 自动计算重叠步长（默认50%重叠）
    step_size = max(max_tokens // 2, 1)  # 保证最小步长为1

    # 边界情况处理
    if total_tokens <= max_tokens:
        return [" ".join(tokens)]

    # 生成滑动窗口块
    start_idx = 0
    while start_idx < total_tokens:
        end_idx = min(start_idx + max_tokens, total_tokens)
        current_chunk = tokens[start_idx:end_idx]

        # 当剩余token不足时，向前扩展窗口
        if len(current_chunk) < max_tokens and start_idx > 0:
            required = max_tokens - len(current_chunk)
            current_chunk = tokens[max(0, start_idx - required):end_idx]

        chunks.append(" ".join(current_chunk))
        start_idx += step_size

        # 防止最后一个块重复
        if end_idx == total_tokens:
            break

    return chunks

def aggregate_embeddings(embeddings: list) -> np.ndarray:
    """对多个嵌入进行平均池化合并"""
    return np.mean(np.vstack(embeddings), axis=0)

def _update_index(state, vector, file_md5, file_path) -> int:
    """更新索引和映射"""
    if state.faiss_index is None:
        state.faiss_index = load_faiss_index()

    # 确保向量是二维的 (n, d)
    if vector.ndim == 1:
        vector = vector.reshape(1, -1)  # 将一维向量转换为二维数组

    state.faiss_index.add(vector)
    doc_id = state.faiss_index.ntotal - 1

    with state._lock:
        state.file_id_map[doc_id] = file_md5
        state.file_path_map[file_md5] = file_path
        state.save_mappings()

    save_faiss_index(state.faiss_index)
    return doc_id


def process_files_in_directory(state, directory_path: str) -> None:
    """处理文件夹中的所有文件"""
    if not os.path.isdir(directory_path):
        logger.error(f"The provided path is not a valid directory: {directory_path}")
        return

    logger.info(f"Processing files in directory: {directory_path}")
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            result = process_local_file(state, file_path)
            logger.info(f"Processing result for {file}: {result}")
