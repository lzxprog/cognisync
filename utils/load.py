import hashlib
import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, Optional

import faiss
import numpy as np
import portalocker
import unicodedata

from utils.faiss_utils import load_faiss_index, save_faiss_index
from config import FILES_PATH, MAPPING_PATH
from utils.sentence_model import get_model, encode_text
from utils.text_processing import extract_text_from_docx, extract_text_from_pdf

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
    """管理索引状态的单例类，优化后版本"""
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
            if Path(MAPPING_PATH).exists():
                with portalocker.Lock(MAPPING_PATH, timeout=5) as f:
                    data = json.load(f)
                    self.file_id_map = {int(k): v for k, v in data['file_id_map'].items()}
                    self.file_path_map = data['file_path_map']
                logger.info("Mappings loaded successfully")
            else:
                self._create_new_mappings()
        except Exception as e:
            logger.error(f"Failed to load mappings: {str(e)}")
            self._create_new_mappings()

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


def process_local_file(file_path: str) -> dict:
    logger.info("Processing local file")
    state = FileIndexState()
    logger.info("Loading index")
    filename = os.path.basename(file_path)

    try:
        # 文本提取与验证
        content = _extract_file_content(file_path)
        logger.info(f"Extracted content from {content}")
        if not content:
            return {"status": "skipped", "reason": "empty_content", "file": filename}

        # MD5计算与重复检查
        file_md5 = calculate_md5_from_text(content)
        logger.info(f"Calculated MD5: {file_md5}")
        if file_md5 in state.file_path_map:
            logger.info(f"File exists: {filename} (MD5: {file_md5})")
            return {"status": "exists", "md5": file_md5, "file": filename}

        # 文本编码
        vector = _encode_file_content(content)

        # 索引更新
        doc_id = _update_index(state, vector, file_md5, file_path)

        return {"status": "success", "md5": file_md5, "id": doc_id, "file": filename}

    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
        return {"status": "error", "reason": str(e), "file": filename}


def _extract_file_content(file_path: str) -> str:
    """提取文件内容，带格式校验"""
    file_ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"Processing {file_path}")
    logger.info(f"Processing {file_ext}")
    handlers = {
        '.docx': extract_text_from_docx,
        '.pdf': extract_text_from_pdf,
        '.txt': lambda p: Path(p).read_text(encoding='utf-8')
    }

    if file_ext not in handlers:
        raise ValueError(f"Unsupported file type: {file_ext}")

    content = handlers[file_ext](file_path)
    if not content.strip():
        raise ValueError("Empty file content")
    return content.strip()


def _encode_file_content(content: str) -> np.ndarray:
    """编码文本内容并进行 L2 归一化"""
    model = get_model()
    vector = encode_text(model, content)
    vector = np.array(vector, dtype=np.float32).reshape(1, -1)
    vector = vector / np.linalg.norm(vector, axis=1, keepdims=True)  # L2 normalization
    return vector


def _update_index(state, vector, file_md5, file_path) -> int:
    """更新索引和映射"""
    if state.faiss_index is None:
        state.faiss_index = load_faiss_index()

    state.faiss_index.add(vector)
    doc_id = state.faiss_index.ntotal - 1

    with state._lock:
        state.file_id_map[doc_id] = file_md5
        state.file_path_map[file_md5] = file_path
        state.save_mappings()

    save_faiss_index(state.faiss_index)
    return doc_id


def process_files_in_directory(directory_path: str) -> None:
    """处理文件夹中的所有文件"""
    if not os.path.isdir(directory_path):
        logger.error(f"The provided path is not a valid directory: {directory_path}")
        return

    logger.info(f"Processing files in directory: {directory_path}")
    processed_files = set()  # 用于存储已处理的文件路径
    # 遍历目录并处理文件
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path not in processed_files:  # 确保文件没有被处理过
                result = process_local_file(file_path)
                logger.info(f"Processing result for {file}: {result}")
                processed_files.add(file_path)  # 记录已处理文件