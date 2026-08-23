from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import requests


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.5",
    description="TikTok Shop销量监控系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# =========================
# Supabase 配置
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

        "version": "0.4.5",

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

@app.get(
    "/debug/env",
    summary="检查环境变量"
)
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

@app.post(
    "/v1/upload/create",
    summary="创建上传批次"
)
def create_upload():

    batch_id = str(
        uuid.uuid4()
    )


    return {

        "status": "success",

        "batch_id": batch_id,

        "created_at":
            datetime.utcnow().isoformat()

    }



# =========================
# 上传HAR文件
# =========================

@app.post(
    "/v1/upload/har",
    summary="上传HAR文件",
    description="上传TikTok Shop HAR文件并保存到Supabase Storage"
)
async def upload_har(
    files: list[UploadFile] = File(
        ...,
        description="HAR文件列表"
    )
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


    result = []


    headers = {

        "Authorization":
            f"Bearer {SUPABASE_SERVICE_KEY}",

        "apikey":
            SUPABASE_SERVICE_KEY

    }


    for file in files:


        content = await file.read()


        filename = (

            datetime.utcnow()
            .strftime("%Y%m%d")

            +

            "/"

            +

            str(uuid.uuid4())

            +

            "_"

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

            filename

        )


        response = requests.post(

            upload_url,

            headers=headers,

            data=content,

            timeout=60

        )


        if response.status_code not in [
            200,
            201
        ]:

            result.append({

                "filename":
                    file.filename,

                "status":
                    "failed",

                "detail":
                    response.text

            })

            continue



        public_url = (

            SUPABASE_URL

            +

            "/storage/v1/object/public/"

            +

            BUCKET_NAME

            +

            "/"

            +

            filename

        )


        result.append({

            "filename":
                file.filename,

            "status":
                "success",

            "size":
                len(content),

            "path":
                filename,

            "public_url":
                public_url

        })


    return {

        "status":
            "success",

        "files":
            result

    }




# =========================
# HAR读取测试
# =========================

class ReadHARRequest(BaseModel):

    url: str



@app.post(
    "/v1/debug/read-har",
    summary="读取HAR测试"
)
def read_har(
    data: ReadHARRequest
):

    try:

        response = requests.get(

            data.url,

            timeout=20

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
# 生成public url测试
# =========================

class PublicURLRequest(BaseModel):

    path: str



@app.post(
    "/v1/upload/public-url",
    summary="生成公开URL"
)
def public_url(
    data: PublicURLRequest
):


    if not SUPABASE_URL:

        raise HTTPException(
            500,
            "SUPABASE_URL missing"
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
