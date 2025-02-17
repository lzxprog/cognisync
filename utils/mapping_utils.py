import json
import logging
import os
from pathlib import Path
from typing import Tuple, Dict
import portalocker
from config import MAPPING_PATH

# 获取日志记录器
logger = logging.getLogger(__name__)

def load_mappings() -> Tuple[Dict[int, str], Dict[str, str]]:
    """安全加载映射文件，支持自动恢复"""
    mapping_path = Path(MAPPING_PATH)
    temp_path = mapping_path.with_suffix('.tmp')

    for retry in range(3):
        try:
            if not mapping_path.exists():
                return {}, {}

            # 带锁读取
            with portalocker.Lock(mapping_path, 'r', timeout=5) as f:
                raw_data = f.read()
                data = json.loads(raw_data)

            # 验证数据结构
            if not isinstance(data, dict) or 'file_id_map' not in data or 'file_path_map' not in data:
                raise ValueError("Invalid mapping structure")

            file_id_map = {int(k): v for k, v in data['file_id_map'].items()}
            file_path_map = data['file_path_map']

            # 验证映射一致性
            for doc_id, md5 in file_id_map.items():
                if md5 not in file_path_map:
                    raise ValueError(f"Inconsistent mapping at doc_id={doc_id}")

            return file_id_map, file_path_map

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Mapping validation failed: {str(e)}")
            if retry == 0 and mapping_path.exists():
                _attempt_mapping_recovery(mapping_path, temp_path)
            else:
                break
        except Exception as e:
            logger.error(f"Unexpected mapping error: {str(e)}")
            break

    logger.critical("Failed to load mappings, returning empty")
    return {}, {}


def save_mappings(file_id_map: Dict[int, str], file_path_map: Dict[str, str]):
    """原子化保存映射文件"""
    mapping_path = Path(MAPPING_PATH)
    temp_path = mapping_path.with_suffix('.tmp')

    try:
        # 先写入临时文件
        data = {
            'file_id_map': {str(k): v for k, v in file_id_map.items()},
            'file_path_map': file_path_map
        }
        json_str = json.dumps(data, indent=2)

        with portalocker.Lock(temp_path, 'w', timeout=10) as f:
            f.write(json_str)

        # 原子替换
        with portalocker.Lock(mapping_path, 'w', timeout=10) as f:
            os.replace(temp_path, mapping_path)

        logger.info(f"Mappings saved (ids={len(file_id_map)}, paths={len(file_path_map)})")

    except Exception as e:
        logger.error(f"Mapping save failed: {str(e)}")
        if temp_path.exists():
            os.remove(temp_path)
        raise


def _attempt_mapping_recovery(mapping_path: Path, temp_path: Path):
    """尝试恢复损坏的映射文件"""
    logger.warning("Attempting mapping recovery...")
    try:
        # 读取原始数据
        with open(mapping_path, 'r') as f:
            raw_data = f.read()

        # 尝试渐进式修复
        repaired = False
        try:
            data = json.loads(raw_data)
            repaired = True
        except json.JSONDecodeError:
            # 尝试补全结尾
            if raw_data.strip().endswith(('}', ']')):
                pass
            else:
                raw_data += '}'
                data = json.loads(raw_data)
                repaired = True

        if repaired:
            backup_path = mapping_path.with_suffix('.bak')
            os.replace(mapping_path, backup_path)
            save_mappings(
                {int(k): v for k, v in data.get('file_id_map', {}).items()},
                data.get('file_path_map', {})
            )
            logger.info("Mapping recovery successful")
        else:
            logger.error("Automatic recovery failed")

    except Exception as e:
        logger.error(f"Recovery attempt failed: {str(e)}")


def validate_mappings(file_id_map: Dict[int, str], file_path_map: Dict[str, str]) -> bool:
    """验证映射一致性"""
    # 检查ID映射的MD5是否都存在路径映射
    missing_md5 = set(file_id_map.values()) - set(file_path_map.keys())
    if missing_md5:
        logger.error(f"Missing {len(missing_md5)} MD5 in path mapping")
        return False

    # 检查路径是否存在
    missing_files = []
    for md5, path in file_path_map.items():
        if not Path(path).exists():
            missing_files.append(path)
    if missing_files:
        logger.warning(f"Missing {len(missing_files)} mapped files")

    return True