from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import uuid
from datetime import datetime

from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.3.0",
    description="TikTok Shop销量监控系统"
)


# =========================
# Supabase
# =========================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

BUCKET_NAME = "har-files"


if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )
else:
    supabase = None



# =========================
# 基础测试
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
# 创建批次
# =========================

@app.post("/v1/batch/create-upload")
def create_upload():

    batch_id = str(uuid.uuid4())

    return {

        "status":"ok",
        "batch_id":batch_id,
        "message":"Upload batch created"

    }



# =========================
# 上传HAR文件
# =========================

@app.post("/v1/upload/har")
async def upload_har(
    files: List[UploadFile] = File(...)
):

    if not supabase:

        return {
            "status":"error",
            "message":"Supabase not configured"
        }


    batch_id = str(uuid.uuid4())


    upload_results = []


    folder = datetime.utcnow().strftime(
        "%Y-%m-%d"
    )


    for file in files:


        file_id = str(uuid.uuid4())

        path = (
            f"{folder}/"
            f"{batch_id}/"
            f"{file_id}_{file.filename}"
        )


        content = await file.read()


        supabase.storage.from_(
            BUCKET_NAME
        ).upload(
            path,
            content,
            {
                "content-type":
                "application/json"
            }
        )


        public_url = (
            SUPABASE_URL
            + "/storage/v1/object/public/"
            + BUCKET_NAME
            + "/"
            + path
        )


        upload_results.append({

            "filename":file.filename,
            "path":path,
            "url":public_url

        })


    return {

        "status":"success",
        "batch_id":batch_id,
        "files":upload_results

    }



# =========================
# 提交文件记录
# =========================

@app.post("/v1/batch/commit-files")
def commit_files(

    batch_id:str,
    files:List[str]

):

    return {

        "status":"ok",
        "batch_id":batch_id,
        "files":files,
        "message":
        "Files committed"

    }
