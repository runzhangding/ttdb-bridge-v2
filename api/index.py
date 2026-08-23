from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
import uuid


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.5.5",
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

BUCKET_NAME = "har-files"



# =========================
# 首页
# =========================

@app.get("/")
def home():

    return {
        "status": "ok",
        "service": "天天爆单 Bridge",
        "version": "0.5.5",
        "docs": "/docs"
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
# 创建批次
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
# 单文件生成上传地址
# =========================


class SignRequest(BaseModel):

    batch_id:str

    filename:str




@app.post("/v1/upload/sign")
def upload_sign(
    data:SignRequest
):


    if not SUPABASE_URL:

        raise HTTPException(
            500,
            "SUPABASE_URL missing"
        )



    path = (

        data.batch_id

        + "/"

        + data.filename

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

        "filename":
            data.filename,

        "path":
            path,

        "upload_url":
            upload_url,

        "public_url":
            public_url

    }




# =========================
# 批量生成上传地址
# =========================


class BatchSignRequest(BaseModel):

    batch_id:str

    filenames:list[str]




@app.post("/v1/upload/batch-sign")
def batch_sign(
    data:BatchSignRequest
):


    if not SUPABASE_URL:

        raise HTTPException(
            500,
            "SUPABASE_URL missing"
        )



    result=[]



    for filename in data.filenames:


        path = (

            data.batch_id

            +

            "/"

            +

            filename

        )


        result.append({

            "filename":

                filename,


            "path":

                path,


            "upload_url":

                SUPABASE_URL

                +

                "/storage/v1/object/"

                +

                BUCKET_NAME

                +

                "/"

                +

                path,


            "public_url":

                SUPABASE_URL

                +

                "/storage/v1/object/public/"

                +

                BUCKET_NAME

                +

                "/"

                +

                path

        })



    return {


        "status":

            "success",


        "batch_id":

            data.batch_id,


        "files":

            result

    }





# =========================
# 提交批次文件
# =========================


class CommitRequest(BaseModel):

    batch_id:str

    files:list[str]




@app.post("/v1/batch/commit-files")
def commit_files(
    data:CommitRequest
):


    return {


        "status":

            "success",


        "batch_id":

            data.batch_id,


        "files":

            data.files,


        "count":

            len(data.files),


        "message":

            "batch committed"

    }
    # =========================
# HAR解析测试
# =========================

class ParseHARRequest(BaseModel):
    url: str


@app.post("/v1/debug/parse-har")
def parse_har(
    data: ParseHARRequest
):

    try:

        response = requests.get(
            data.url,
            timeout=60
        )


        if response.status_code != 200:

            return {

                "status": "error",

                "http_status":
                    response.status_code

            }


        import json


        har = json.loads(
            response.text
        )


        entries = (
            har
            .get("log", {})
            .get("entries", [])
        )


        return {

            "status":
                "success",

            "entries":
                len(entries),

            "size":
                len(response.content),

            "message":
                "HAR读取成功"

        }


    except Exception as e:


        return {

            "status":
                "error",

            "detail":
                str(e)

        }
