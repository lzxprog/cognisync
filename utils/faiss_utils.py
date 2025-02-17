import logging
import faiss
import portalocker
import os
from pathlib import Path
from typing import Optional
from config import FAISS_INDEX_PATH
import time

# 获取日志记录器
logger = logging.getLogger(__name__)

# 内存缓存变量
_faiss_index_cache: Optional[faiss.Index] = None
_cache_metadata: dict = {}


def load_faiss_index(use_cache: bool = True) -> faiss.Index:
    """安全加载FAISS索引，支持内存缓存和自动恢复"""
    global _faiss_index_cache, _cache_metadata

    if use_cache and _faiss_index_cache is not None:
        if _validate_cache():
            return _faiss_index_cache

    try:
        index_path = Path(FAISS_INDEX_PATH)
        if not index_path.exists():
            logger.warning("FAISS index not found, creating new index")
            return _create_new_index()

        # 带锁读取
        with portalocker.Lock(index_path, 'rb', timeout=10) as f:
            index = faiss.read_index(str(index_path))
            current_mtime = os.path.getmtime(index_path)

        # 验证索引完整性
        if index.ntotal < 0:
            raise RuntimeError("Invalid index structure detected")

        # 更新缓存
        if use_cache:
            _faiss_index_cache = index
            _cache_metadata = {
                'mtime': current_mtime,
                'size': index.ntotal
            }
        return index

    except Exception as e:
        logger.error(f"Index loading failed: {str(e)}")
        # 捕获一般异常，而不是 faiss.FaissException
        if isinstance(e, RuntimeError):
            logger.warning("Attempting index recovery...")
            return _handle_corrupted_index()
        raise


def load_faiss_index_with_retry(use_cache: bool = True, max_retries: int = 3) -> faiss.Index:
    """尝试加载FAISS索引，处理文件锁问题并进行重试"""
    retries = 0
    while retries < max_retries:
        try:
            return load_faiss_index(use_cache)
        except portalocker.LockException as e:
            retries += 1
            logger.warning(f"Lock acquisition failed, retrying {retries}/{max_retries}...")
            time.sleep(2)  # 等待2秒后重试
    logger.critical("Failed to acquire lock after multiple attempts")
    raise RuntimeError("Failed to load FAISS index due to file lock issues")


def save_faiss_index(index: faiss.Index):
    """安全保存FAISS索引，带原子写入和备份机制"""
    index_path = Path(FAISS_INDEX_PATH)
    temp_path = index_path.with_suffix('.tmp')
    backup_path = index_path.with_suffix('.bak')

    try:
        # 检查目标路径是否可写
        if not index_path.parent.exists() or not os.access(index_path.parent, os.W_OK):
            logger.error(f"Cannot write to directory: {index_path.parent}")
            raise PermissionError(f"Cannot write to directory: {index_path.parent}")

        # 先写入临时文件
        logger.info(f"Writing FAISS index to temporary file: {temp_path}")
        with portalocker.Lock(temp_path, 'wb', timeout=15) as f:
            if index.ntotal < 0:
                raise RuntimeError("Invalid index structure detected")
            faiss.write_index(index, str(temp_path))

        # 原子替换操作
        if backup_path.exists():
            os.remove(backup_path)
        if index_path.exists():
            os.rename(index_path, backup_path)
        os.rename(temp_path, index_path)

        # 清理旧备份
        if backup_path.exists():
            os.remove(backup_path)

        logger.info(f"Index saved successfully (ntotal={index.ntotal}) to {index_path}")

    except portalocker.LockException as e:
        logger.error(f"Failed to acquire lock for {temp_path}: {e}")
        raise RuntimeError(f"Index save failed due to lock timeout: {e}") from e
    except Exception as e:
        logger.error(f"Index save failed: {e}", exc_info=True)
        # 如果保存失败，尝试恢复备份
        _restore_backup(backup_path, index_path)
        raise


def _create_new_index() -> faiss.Index:
    """创建新索引时动态获取维度"""
    from utils.sentence_model import get_model  # 延迟导入避免循环依赖
    try:
        model = get_model()
        sample_vector = model.encode(["sample text"])[0]
        dimension = len(sample_vector)
        index = faiss.IndexFlatIP(dimension)
        logger.info(f"Created new FAISS index (dim={dimension})")
        return index
    except Exception as e:
        logger.error("Failed to create new index", exc_info=True)
        raise


def _validate_cache() -> bool:
    """验证缓存有效性"""
    global _cache_metadata

    if not Path(FAISS_INDEX_PATH).exists():
        return False

    current_mtime = os.path.getmtime(FAISS_INDEX_PATH)
    current_size = _faiss_index_cache.ntotal if _faiss_index_cache else 0

    return (
            _cache_metadata.get('mtime') == current_mtime and
            _cache_metadata.get('size') == current_size
    )


def _handle_corrupted_index() -> faiss.Index:
    """处理索引损坏情况"""
    backup_path = Path(FAISS_INDEX_PATH).with_suffix('.bak')
    if backup_path.exists():
        logger.warning("Restoring from backup...")
        os.replace(backup_path, FAISS_INDEX_PATH)
        return load_faiss_index(use_cache=False)
    logger.error("No backup available, creating new index")
    return _create_new_index()


def _restore_backup(backup_path: Path, target_path: Path):
    """尝试恢复备份"""
    try:
        if backup_path.exists():
            os.replace(backup_path, target_path)
            logger.warning("Restored from backup")
        else:
            logger.error("No backup available")
    except Exception as e:
        logger.critical(f"Backup restoration failed: {e}", exc_info=True)