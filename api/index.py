from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
from supabase import create_client


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


supabase = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )



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


        if not supabase:

            raise Exception(
                "Supabase client not initialized"
            )


        url = data.url


        # 提取storage路径

        if "/har-files/" not in url:

            raise Exception(
                "Invalid HAR public url"
            )


        path = url.split(
            "/har-files/"
        )[1]


        # 使用service key读取

        file_bytes = (

            supabase.storage

            .from_(BUCKET_NAME)

            .download(path)

        )


        return {


            "status":"success",


            "content_length":

                len(file_bytes),


            "message":

                "HAR download success via Supabase SDK"

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
