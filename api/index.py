from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import requests
import json

from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.3",
    description="TikTok Shop销量监控系统"
)


# =========================
# Supabase 配置
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
        "service":"天天爆单 Bridge"
    }



@app.get("/health")
def health():

    return {
        "status":"healthy"
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

        "bucket":BUCKET_NAME,

        "created_at":datetime.utcnow().isoformat()

    }



# =========================
# 上传HAR文件
# =========================

@app.post("/v1/upload/har")
async def upload_har(
    files:list[UploadFile]=File(...)
):

    if supabase is None:

        raise HTTPException(
            status_code=500,
            detail="Supabase not configured"
        )


    batch_id=str(uuid.uuid4())

    uploaded=[]


    for file in files:


        content=await file.read()


        path=(

            datetime.utcnow().strftime("%Y%m%d")

            +"/"

            +batch_id

            +"/"

            +file.filename

        )


        supabase.storage.from_(BUCKET_NAME).upload(
            path,
            content
        )


        uploaded.append({

            "filename":file.filename,

            "path":path

        })


    return {

        "status":"success",

        "batch_id":batch_id,

        "files":uploaded

    }



# =========================
# 获取文件路径
# =========================

class PathRequest(BaseModel):

    batch_id:str

    filename:str



@app.post("/v1/upload/path")
def upload_path(data:PathRequest):


    path=(

        datetime.utcnow().strftime("%Y%m%d")

        +"/"

        +data.batch_id

        +"/"

        +data.filename

    )


    return {

        "status":"success",

        "path":path,

        "bucket":BUCKET_NAME

    }




# =========================
# 获取public_url
# =========================

class PublicURLRequest(BaseModel):

    batch_id:str

    filename:str



@app.post("/v1/upload/public-url")
def public_url(data:PublicURLRequest):


    path=(

        datetime.utcnow().strftime("%Y%m%d")

        +"/"

        +data.batch_id

        +"/"

        +data.filename

    )


    url=(

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
# Debug读取HAR
# =========================

class ReadHARRequest(BaseModel):

    url:str




@app.post("/v1/debug/read-har")
def read_har(data:ReadHARRequest):


    try:


        response=requests.get(

            data.url,

            timeout=30

        )


        if response.status_code != 200:


            raise HTTPException(

                status_code=500,

                detail=f"download failed:{response.status_code}"

            )



        har_data=json.loads(

            response.text

        )



        entries=(

            har_data

            .get("log",{})

            .get("entries",[])

        )



        return {

            "status":"success",

            "url":data.url,

            "entries_count":len(entries),

            "message":"HAR read success"

        }



    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
