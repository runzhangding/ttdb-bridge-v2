from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import requests


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.7",
    description="TikTok Shop销量监控系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# =========================
# Supabase配置
# =========================

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL"
)

SUPABASE_SERVICE_KEY = os.environ.get(
    "SUPABASE_SERVICE_KEY"
)

BUCKET_NAME = "har-files"



# =========================
# 首页
# =========================

@app.get("/")
def home():

    return {

        "status": "ok",

        "service": "天天爆单 Bridge",

        "version": "0.4.7",

        "docs": "/docs"

    }



# =========================
# 健康检查
# =========================

@app.get("/health")
def health():

    return {

        "status": "healthy"

    }



# =========================
# 环境检测
# =========================

@app.get("/debug/env")
def debug_env():

    return {

        "supabase_url":

            SUPABASE_URL,

        "service_key_exists":

            bool(SUPABASE_SERVICE_KEY),

        "bucket":

            BUCKET_NAME

    }



# =========================
# 创建上传批次
# =========================

@app.post("/v1/upload/create")
def create_upload():

    batch_id = str(uuid.uuid4())


    return {

        "status": "success",

        "batch_id": batch_id,

        "created_at":
            datetime.utcnow().isoformat()

    }



# =========================
# 获取Supabase上传地址
# =========================

class SignRequest(BaseModel):

    batch_id: str

    filename: str



@app.post("/v1/upload/sign")
def create_upload_sign(
    data: SignRequest
):

    if not SUPABASE_URL:

        raise HTTPException(
            500,
            "SUPABASE_URL missing"
        )


    if not SUPABASE_SERVICE_KEY:

        raise HTTPException(
            500,
            "SUPABASE_SERVICE_KEY missing"
        )


    path = (
        data.batch_id
        +
        "/"
        +
        data.filename
    )


    url = (

        SUPABASE_URL

        +

        "/storage/v1/object/"

        +

        BUCKET_NAME

        +

        "/"

        +

        path

    )


    public_url = (

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

        "upload_url":url,

        "public_url":public_url

    }



# =========================
# 提交文件列表
# =========================

class CommitFilesRequest(BaseModel):

    batch_id:str

    files:list[str]



@app.post("/v1/batch/commit-files")
def commit_files(
    data:CommitFilesRequest
):


    return {

        "status":"success",

        "batch_id":
            data.batch_id,

        "files":
            data.files,

        "message":
            "files committed"

    }



# =========================
# HAR读取测试
# =========================

class ReadHARRequest(BaseModel):

    url:str



@app.post("/v1/debug/read-har")
def read_har(
    data:ReadHARRequest
):

    try:

        response = requests.get(
            data.url,
            timeout=20
        )


        return {

            "status":"success",

            "http_status":
                response.status_code,

            "content_length":
                len(response.content),

            "content_type":
                response.headers.get(
                    "content-type"
                )

        }


    except Exception as e:


        return {

            "status":"error",

            "detail":
                str(e)

        }
