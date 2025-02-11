from fastapi import FastAPI
from routes import upload, query, destroy

app = FastAPI(title="Cognisync - AI Data Bridge")

# Include API routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(destroy.router, prefix="/destroy", tags=["Destroy"])

@app.get("/")
def root():
    return {"message": "Welcome to Cognisync - AI Data Bridge"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)