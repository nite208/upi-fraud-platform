import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Base paths ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "ml" / "models"

# ── Database ──────────────────────────────────────────────────────────────────
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB       = os.getenv("POSTGRES_DB", "frauddb")
POSTGRES_USER     = os.getenv("POSTGRES_USER", "frauduser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fraudpass123")
DATABASE_URL      = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ── Neo4j ─────────────────────────────────────────────────────────────────────
NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "fraudpass123")

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_URL  = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# ── Kafka ─────────────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_TOPIC_TRANSACTIONS = "upi.transactions"
KAFKA_TOPIC_ALERTS       = "upi.fraud-alerts"
KAFKA_TOPIC_GRAPH        = "upi.graph-events"
KAFKA_TOPIC_DLQ          = "upi.dlq"

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "phi3:mini")

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8001))

# ── MLflow ────────────────────────────────────────────────────────────────────
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

# ── App ───────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_in_production")
DEBUG      = os.getenv("DEBUG", "true").lower() == "true"
LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")

# ── Risk scoring thresholds ───────────────────────────────────────────────────
SCORE_SAFE_MAX   = 30.0   # 0-30   → SAFE
SCORE_REVIEW_MAX = 69.0   # 31-69  → REVIEW
# 70-100 → BLOCK

# ── Ensemble weights ──────────────────────────────────────────────────────────
WEIGHT_ML      = 0.40
WEIGHT_GRAPH   = 0.35
WEIGHT_ANOMALY = 0.25

# ── SLA deadlines (minutes) ───────────────────────────────────────────────────
SLA_BLOCK_MINUTES        = 120  # 2 hours
SLA_HIGH_REVIEW_MINUTES  = 30   # 30 minutes
SLA_REVIEW_MINUTES       = 240  # 4 hours

# ── Model paths ───────────────────────────────────────────────────────────────
XGB_MODEL_PATH         = MODELS_DIR / "xgb_fraud_model.pkl"
RF_MODEL_PATH          = MODELS_DIR / "rf_fraud_model.pkl"
FEATURE_SCALER_PATH    = MODELS_DIR / "feature_scaler.pkl"
MODEL_METADATA_PATH    = MODELS_DIR / "model_metadata.json"
ISO_FOREST_PATH        = MODELS_DIR / "isolation_forest.pkl"
AUTOENCODER_PATH       = MODELS_DIR / "autoencoder.pt"
ANOMALY_SCALER_PATH    = MODELS_DIR / "anomaly_scaler.pkl"
GCN_MODEL_PATH         = MODELS_DIR / "gcn_model.pt"
NODE_EMBEDDINGS_PATH   = MODELS_DIR / "node_embeddings.npy"
VPA_TO_ID_PATH         = MODELS_DIR / "vpa_to_id.pkl"
GRAPH_METADATA_PATH    = MODELS_DIR / "graph_metadata.json"

# ── Feature list (must match training) ───────────────────────────────────────
FEATURES = [
    'amount', 'amount_log', 'hour', 'day_of_week',
    'is_weekend', 'is_night', 'is_round_amount',
    'has_merchant', 'upi_app_encoded',
    'sender_txn_count', 'sender_avg_amount', 'amount_vs_avg',
    'is_new_receiver', 'device_shared', 'receiver_count',
    'device_vpa_count'
]

UPI_APP_MAP = {
    'PhonePe': 0, 'GooglePay': 1, 'Paytm': 2,
    'BHIM': 3, 'AmazonPay': 4
}