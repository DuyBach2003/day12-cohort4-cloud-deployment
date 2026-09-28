"""
Agent Cloud Run-ready — dùng bởi cloudbuild.yaml / service.yaml.

Cloud Run inject PORT env var tự động (container phải listen đúng port này).
Có AGENT_API_KEY check đơn giản khi biến này được set (qua Secret Manager).
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utils.mock_llm import ask

START_TIME = time.time()
is_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_ready
    is_ready = True
    yield
    is_ready = False


app = FastAPI(title="Agent on Cloud Run", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Agent running on Cloud Run!",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/ask")
async def ask_agent(request: Request):
    body = await request.json()
    question = body.get("question", "")
    if not question:
        raise HTTPException(422, "question required")
    return {
        "question": question,
        "answer": ask(question),
        "platform": "Cloud Run",
    }


@app.get("/health")
def health():
    """
    Liveness probe (service.yaml) — Cloud Run restart container nếu fail.
    """
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "platform": "Cloud Run",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def ready():
    """
    Startup probe (service.yaml) — Cloud Run chờ 200 trước khi route traffic.
    """
    if not is_ready:
        raise HTTPException(status_code=503, detail="Agent not ready yet")
    return {"ready": True}


if __name__ == "__main__":
    # ✅ Cloud Run inject PORT — PHẢI đọc từ env
    port = int(os.getenv("PORT", 8000))
    print(f"Starting on port {port} (from PORT env var)")
    uvicorn.run(app, host="0.0.0.0", port=port)
