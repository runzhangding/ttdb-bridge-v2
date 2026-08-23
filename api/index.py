from fastapi import FastAPI
from typing import List
import os
import uuid
from datetime import datetime

from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.2.0",
    description="TikTok Shop销量监控系统"
)


# -------------------------
# Supabase 配置
# -------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )
else:
    supabase = None



# -------------------------
# 基础测试
# -------------------------

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



# -------------------------
# 创建上传任务
# -------------------------

@app.post("/v1/batch/create-upload")
def create_upload():

    batch_id = str(uuid.uuid4())

    return {
        "status": "ok",
        "batch_id": batch_id,
        "message": "Upload batch created"
    }



# -------------------------
# 提交已上传文件
# -------------------------

@app.post("/v1/batch/commit-files")
def commit_files(
    batch_id: str,
    files: List[str]
):

    return {
        "status": "ok",
        "batch_id": batch_id,
        "files": files,
        "message": "Files committed"
    }
