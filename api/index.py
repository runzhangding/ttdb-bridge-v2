from fastapi import FastAPI

app = FastAPI(
    title="天天爆单 Bridge",
    version="1.0.0",
    description="TikTok Shop销量监控系统"
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "天天爆单 Bridge V2 running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
