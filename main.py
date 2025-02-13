from fastapi import FastAPI
from routes import upload, query  # 导入上传和查询路由
from config import ENVIRONMENT  # 从配置中导入环境设置
import logging
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI()

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 根据不同环境设置配置
if ENVIRONMENT == "production":
    logger.info("Running in production mode")
elif ENVIRONMENT == "development":
    logger.info("Running in development mode")
else:
    logger.info("Running in default mode")

# 添加 API 路由
app.include_router(upload.router, tags=["File Upload"])
app.include_router(query.router,  tags=["AI Querying"])

# 首页测试路由
@app.get("/")
def read_root():
    return {"message": "Welcome to cognisync API!"}

# 启动 FastAPI 应用
if __name__ == "__main__":
    logger.info("Starting the application...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)