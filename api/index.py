from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
from datetime import datetime

from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.0",
    description="TikTok Shop销量监控系统"
)


# =========================
# Supabase配置
# =========================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

BUCKET_NAME = "har-files"


supabase = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )



# =========================
# 基础接口
# =========================


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



# =========================
# 创建上传任务
# =========================


@app.post("/v1/upload/create")
def create_upload():

    batch_id = str(uuid.uuid4())


    return {
        "status": "success",
        "batch_id": batch_id,
        "bucket": BUCKET_NAME,
        "created_at": datetime.utcnow().isoformat()
    }



# =========================
# 生成上传路径
# =========================


class UploadPathRequest(BaseModel):
    batch_id: str
    filename: str



@app.post("/v1/upload/path")
def create_upload_path(
    data: UploadPathRequest
):

    if not data.filename.endswith(".har"):
        raise HTTPException(
            status_code=400,
            detail="Only HAR files allowed"
        )


    path = (
        datetime.utcnow().strftime("%Y%m%d")
        +
        "/"
        +
        data.batch_id
        +
        "/"
        +
        data.filename
    )


    return {
        "status": "success",
        "path": path,
        "bucket": BUCKET_NAME
    }



# =========================
# 上传完成通知
# =========================


class CommitRequest(BaseModel):
    batch_id: str
    files: list[str]



@app.post("/v1/upload/commit")
def commit_upload(
    data: CommitRequest
):

    return {
        "status": "success",
        "batch_id": data.batch_id,
        "files": data.files,
        "message": "Upload completed"
    }
    @app.post("/v1/upload/public-url")
def public_url(
    batch_id:str,
    filename:str
):

    path = (
        datetime.utcnow().strftime("%Y%m%d")
        +
        "/"
        +
        batch_id
        +
        "/"
        +
        filename
    )

    url = (
        SUPABASE_URL
        +
        "/storage/v1/object/public/"
        +
        BUCKET_NAME
        +
        "/"
        +
        path
    )


    return {
        "status":"success",
        "path":path,
        "public_url":url
    }
