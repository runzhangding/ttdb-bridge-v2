from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import requests


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.5.3",
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
        "version": "0.5.3",
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

        "supabase_url": SUPABASE_URL,

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

        "status":
            "success",

        "batch_id":
            batch_id,

        "created_at":
            datetime.utcnow().isoformat()

    }



# =========================
# 上传 HAR
# 单文件测试版
# =========================

@app.post("/v1/upload/har")
async def upload_har(

    file: UploadFile = File(
        ...,
        description="上传TikTok Shop HAR文件"
    )

):


    if not SUPABASE_URL:

        raise HTTPException(
            status_code=500,
            detail="SUPABASE_URL missing"
        )


    if not SUPABASE_SERVICE_KEY:

        raise HTTPException(
            status_code=500,
            detail="SUPABASE_SERVICE_KEY missing"
        )


    batch_id = str(uuid.uuid4())


    content = await file.read()


    path = (
        batch_id
        +
        "/"
        +
        file.filename
    )


    upload_url = (

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


    headers = {

        "Authorization":
            f"Bearer {SUPABASE_SERVICE_KEY}",

        "apikey":
            SUPABASE_SERVICE_KEY,

        "Content-Type":
            "application/octet-stream"

    }


    response = requests.post(

        upload_url,

        headers=headers,

        data=content,

        timeout=300

    )


    if response.status_code not in [200,201]:


        raise HTTPException(

            status_code=500,

            detail=response.text

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

        "status":
            "success",

        "batch_id":
            batch_id,

        "filename":
            file.filename,

        "path":
            path,

        "public_url":
            public_url,

        "size":
            len(content)

    }
    # =========================
# HAR读取测试
# =========================

class ReadHARRequest(BaseModel):

    url: str



@app.post("/v1/debug/read-har")
def read_har(
    data: ReadHARRequest
):

    try:

        response = requests.get(
            data.url,
            timeout=30
        )


        return {

            "status":
                "success",

            "http_status":
                response.status_code,

            "content_length":
                len(response.content),

            "content_type":
                response.headers.get(
                    "content-type"
                ),

            "message":
                "HAR download success"

        }


    except Exception as e:


        return {

            "status":
                "error",

            "detail":
                str(e)

        }




# =========================
# public url测试
# =========================

class PublicURLRequest(BaseModel):

    path: str



@app.post("/v1/upload/public-url")
def public_url(
    data: PublicURLRequest
):

    if not SUPABASE_URL:

        raise HTTPException(

            status_code=500,

            detail="SUPABASE_URL missing"

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

        data.path

    )


    return {

        "status":

            "success",


        "public_url":

            url

    }
