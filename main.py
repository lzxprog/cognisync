import logging
import uvicorn
from fastapi import FastAPI
from config import ENVIRONMENT, FILES_PATH
from logging_set_up import configure_logging
from routes import query
from utils.load import process_files_in_directory, FileIndexState


# 环境判断函数
def get_environment_log():
    if ENVIRONMENT == "production":
        return "Running in production mode"
    elif ENVIRONMENT == "development":
        return "Running in development mode"
    return "Running in default mode"


# 初始化函数
def initialize():
    # 配置日志
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info(get_environment_log())

    # 初始化索引
    state = FileIndexState()

    # 加载本地知识库
    process_files_in_directory(state,FILES_PATH)



# 创建 FastAPI 应用实例
app = FastAPI()

# 包含路由
app.include_router(query.router, tags=["AI Querying"])


# 首页测试路由
@app.get("/")
def read_root():
    return {"message": "Welcome to cognisync API!"}


# 主函数
def main():
    # 初始化配置
    initialize()

    # 启动 FastAPI 应用
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# 启动 FastAPI 应用
if __name__ == "__main__":
    main()