import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger().handlers[0].stream.reconfigure(encoding='utf-8')

from fastapi import FastAPI
from routes import upload, query, destroy

app = FastAPI(title="Cognisync - AI Data Bridge")

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(destroy.router, prefix="/destroy", tags=["Destroy"])

@app.get("/")
def root():
    return {"message": "Welcome to Cognisync - AI Data Bridge"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)  # 关闭 Uvicorn 默认日志