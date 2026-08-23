from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
import os
import uuid


app = FastAPI(
    title="天天爆单 Bridge",
    version="0.4.2",
    description="TikTok Shop销量监控系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# =========================
# Supabase配置
# =========================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

BUCKET_NAME = "har-files"


# =========================
# 首页
# =========================

@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "天天爆单 Bridge",
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
# 环境测试
# =========================

@app.get("/debug/env")
def debug_env():

    return {

        "supabase_url":
            SUPABASE_URL,

        "service_key_exists":
            bool(SUPABASE_SERVICE_KEY)

    }



# =========================
# HAR读取测试
# =========================


class ReadHARRequest(BaseModel):

    url:str



@app.post("/v1/debug/read-har")
def read_har(data:ReadHARRequest):

    return {

        "status":"success",

        "url":data.url,

        "message":
        "public_url received"

    }
