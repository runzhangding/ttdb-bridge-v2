from fastapi import FastAPI, UploadFile, File


app = FastAPI(
    title="天天爆单 Bridge",
    version="1.0.0",
    description="TikTok Shop销量监控系统"
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "天天爆单 Bridge V2 running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_har(file: UploadFile = File(...)):

    content = await file.read()

    return {
        "status": "success",
        "filename": file.filename,
        "size": len(content),
        "message": "HAR文件接收成功"
    }
