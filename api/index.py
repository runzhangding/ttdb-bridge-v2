from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import requests


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.3",
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

        "status":"ok",

        "service":"天天爆单 Bridge",

        "version":"0.4.3",

        "docs":"/docs"

    }



# =========================
# 健康检查
# =========================

@app.get("/health")
def health():

    return {

        "status":"healthy"

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

        "status":"success",

        "batch_id":batch_id,

        "created_at":
            datetime.utcnow().isoformat()

    }



# =========================
# 上传HAR文件
# =========================

@app.post("/v1/upload/har")
async def upload_har(
    files:list[UploadFile]=File(...)
):

    result=[]


    for file in files:

        content = await file.read()


        result.append({

            "filename":

                file.filename,


            "size":

                len(content)

        })


    return {

        "status":"success",

        "files":result

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


        if not SUPABASE_URL:

            raise Exception(
                "SUPABASE_URL missing"
            )


        if not SUPABASE_SERVICE_KEY:

            raise Exception(
                "SUPABASE_SERVICE_KEY missing"
            )


        url = data.url


        if "/har-files/" not in url:

            raise Exception(
                "Invalid HAR public url"
            )


        # 提取文件路径

        path = url.split(
            "/har-files/"
        )[1]


        # Supabase Storage REST地址

        storage_url = (

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

                "Bearer "

                +

                SUPABASE_SERVICE_KEY,


            "apikey":

                SUPABASE_SERVICE_KEY

        }



        response = requests.get(

            storage_url,

            headers=headers,

            timeout=30

        )


        if response.status_code != 200:

            raise Exception(

                response.text

            )


        return {


            "status":"success",


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


            "status":"error",


            "detail":

                str(e)

        }





# =========================
# 生成public url测试
# =========================

class PublicURLRequest(BaseModel):

    path:str



@app.post("/v1/upload/public-url")
def public_url(
    data:PublicURLRequest
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


        "status":"success",


        "public_url":

            url

    }
