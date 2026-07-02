import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# ── Local imports ─────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from models.schemas import HealthResponse
from database.timescale import check_connection as check_db
from database.neo4j_client import check_connection as check_neo4j
from engines.fraud_engine import _load_models as load_fraud_models, models_loaded

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── Startup / shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting UPI Fraud Detection Platform...")
    # Pre-load ML models at startup
    try:
        load_fraud_models()
        logger.info("✓ Fraud models loaded")
    except Exception as e:
        logger.warning(f"Model pre-load failed (will load on first request): {e}")

    # Check DB connections
    if check_db():
        logger.info("✓ TimescaleDB connected")
    else:
        logger.warning("⚠ TimescaleDB not available")

    if check_neo4j():
        logger.info("✓ Neo4j connected")
    else:
        logger.warning("⚠ Neo4j not available")

    logger.info("✓ Platform ready")
    yield
    logger.info("Shutting down...")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="UPI Fraud Detection & Risk Intelligence Platform",
    description="AI-powered real-time fraud detection for UPI transactions",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ───────────────────────────────────────────────────────────
from api.transactions import router as txn_router
from api.cases        import router as cases_router
from api.graph        import router as graph_router
from api.analytics    import router as analytics_router

app.include_router(txn_router,       prefix="/api/v1", tags=["Transactions"])
app.include_router(cases_router,     prefix="/api/v1", tags=["Cases"])
app.include_router(graph_router,     prefix="/api/v1", tags=["Graph"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    import redis as redis_lib
    import httpx

    # Redis
    try:
        r = redis_lib.from_url(config.REDIS_URL)
        r.ping()
        redis_status = "up"
    except Exception:
        redis_status = "down"

    # Kafka
    try:
        from streaming.kafka_producer import check_connection
        kafka_status = "up" if check_connection() else "down"
    except Exception:
        kafka_status = "down"

    # Ollama
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")
            ollama_status = "up" if r.status_code == 200 else "down"
    except Exception:
        ollama_status = "down"

    return HealthResponse(
        status      = "healthy",
        timescaledb = "up" if check_db()    else "down",
        neo4j       = "up" if check_neo4j() else "down",
        redis       = redis_status,
        kafka       = kafka_status,
        ollama      = ollama_status,
        models      = "loaded" if models_loaded() else "not loaded",
        timestamp   = datetime.utcnow()
    )

@app.get("/")
async def root():
    return {
        "platform": "UPI Fraud Detection & Risk Intelligence",
        "version":  "1.0.0",
        "docs":     "/docs",
        "health":   "/health"
    }

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config.LOG_LEVEL.lower()
    )