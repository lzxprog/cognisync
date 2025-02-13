from fastapi import FastAPI
from routes import upload, query  # 导入上传和查询路由
from config import ENVIRONMENT  # 从配置中导入环境设置

# 创建 FastAPI 应用实例
app = FastAPI()

# 根据不同环境设置配置
if ENVIRONMENT == "production":
    print("Running in production mode")
elif ENVIRONMENT == "development":
    print("Running in development mode")
else:
    print("Running in default mode")

# 添加 API 路由
app.include_router(upload.router, prefix="/upload", tags=["File Upload"])
app.include_router(query.router, prefix="/query", tags=["AI Querying"])

# 首页测试路由
@app.get("/")
def read_root():
    return {"message": "Welcome to Cognisync API!"}
