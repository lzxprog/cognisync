import logging

import uvicorn
from fastapi import FastAPI
from config import ENVIRONMENT, FILES_PATH  # 从配置中导入环境设置
from logging_set_up import configure_logging
from routes import query  # 导入查询路由
from utils.load import process_files_in_directory

# 加载日志配置
configure_logging()  # 调用日志配置函数

# 获取日志记录器
logger = logging.getLogger(__name__)

# 根据不同环境设置配置
if ENVIRONMENT == "production":
    logger.info("Running in production mode")
elif ENVIRONMENT == "development":
    logger.info("Running in development mode")
else:
    logger.info("Running in default mode")

# 加载本地知识库
process_files_in_directory(FILES_PATH)

# 创建 FastAPI 应用实例
app = FastAPI()

# 添加 API 路由
app.include_router(query.router, tags=["AI Querying"])

# 首页测试路由
@app.get("/")
def read_root():
    return {"message": "Welcome to cognisync API!"}

# 启动 FastAPI 应用
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)