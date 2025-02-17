import logging
import os

from config import LOG_STORAGE_PATH


def configure_logging(log_file=LOG_STORAGE_PATH, log_level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建日志处理器（文件）
    file_handler = logging.FileHandler(log_file, encoding='utf-8')  # 指定编码为 UTF-8
    file_handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # 配置根日志记录器
    logging.basicConfig(level=log_level, handlers=[file_handler, console_handler])