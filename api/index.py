from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import uuid
from datetime import datetime
from supabase import create_client


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.3.1",
    description="TikTok Shop销量监控系统"
)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

BUCKET_NAME = "har-files"


supabase = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )



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



@app.post("/v1/upload/har")
async def upload_har(
    files: List[UploadFile] = File(
        ...,
        description="上传HAR文件，可多选"
    )
):

    batch_id = str(uuid.uuid4())

    result = []


    for file in files:

        content = await file.read()


        filename = (
            datetime.utcnow().strftime("%Y%m%d")
            +
            "/"
            +
            batch_id
            +
            "/"
            +
            file.filename
        )


        if supabase:

            supabase.storage.from_(
                BUCKET_NAME
            ).upload(
                filename,
                content
            )


        result.append({
            "name":file.filename,
            "size":len(content)
        })


    return {
        "status":"success",
        "batch_id":batch_id,
        "files":result
    }
