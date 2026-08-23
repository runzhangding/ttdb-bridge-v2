from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
import json
import requests
from datetime import datetime

from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.5.0",
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
        "status":"ok",
        "message":"天天爆单 Bridge running"
    }



@app.get("/health")
def health():

    return {
        "status":"healthy"
    }



# =========================
# 创建上传任务
# =========================


@app.post("/v1/upload/create")
def create_upload():

    batch_id = str(uuid.uuid4())

    return {

        "status":"success",

        "batch_id":batch_id,

        "bucket":BUCKET_NAME,

        "created_at":
            datetime.utcnow().isoformat()

    }



# =========================
# 生成文件路径
# =========================


class PathRequest(BaseModel):

    batch_id:str

    filename:str



@app.post("/v1/upload/path")
def upload_path(
    data:PathRequest
):

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

        "status":"success",

        "path":path,

        "bucket":BUCKET_NAME

    }



# =========================
# 生成公开URL
# =========================


@app.post("/v1/upload/public-url")
def public_url(
    data:PathRequest
):


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




# =========================
# 新增：
# HAR读取测试
# =========================


class ReadHarRequest(BaseModel):

    url:str



@app.post("/v1/debug/read-har")
def read_har(
    data:ReadHarRequest
):


    try:


        response = requests.get(
            data.url,
            timeout=60
        )


        if response.status_code != 200:

            raise HTTPException(

                status_code=400,

                detail="HAR download failed"

            )


        content = response.content


        size = len(content)


        har = json.loads(
            content.decode(
                "utf-8",
                errors="ignore"
            )
        )


        entries = 0


        if "log" in har:

            entries = len(
                har["log"].get(
                    "entries",
                    []
                )
            )


        return {


            "status":"success",

            "size":size,

            "entries":entries


        }


    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
