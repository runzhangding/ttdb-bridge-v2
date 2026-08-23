from fastapi import FastAPI, UploadFile, File
from typing import List


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.1.0",
    description="TikTok Shop销量监控系统"
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "天天爆单 Bridge running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/v1/batch/commit-files")
async def commit_files(
    files: List[UploadFile] = File(...)
):

    result = []

    for file in files:
        content = await file.read()

        result.append({
            "filename": file.filename,
            "size": len(content)
        })


    return {
        "status": "success",
        "count": len(result),
        "files": result,
        "message": "HAR批次接收成功"
    }
