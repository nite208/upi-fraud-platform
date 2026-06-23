# 🛡️ AI-Powered UPI Fraud Detection & Risk Intelligence Platform

> A production-grade fintech intelligence platform that detects fraudulent UPI transactions, identifies mule accounts, discovers fraud rings, and provides explainable AI-powered investigations.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

---

## 🧠 What it does

| Capability | Technology |
|---|---|
| Real-time fraud scoring | XGBoost + Random Forest ensemble |
| Fraud ring detection | Graph Neural Networks (GCN, GAT, TGN) |
| Anomaly detection | Isolation Forest + Autoencoder + LSTM |
| LLM investigation assistant | Ollama + Llama 3.1 (local, free) |
| RAG-powered case search | LangChain + ChromaDB |
| Real-time streaming | Apache Kafka + Flink |
| Graph database | Neo4j Community |
| Model monitoring | MLflow + Evidently AI |

---

## 🏗️ Architecture

```
Client (React Dashboard)
        ↓
API Gateway (FastAPI + Presidio PII masking)
        ↓
Kafka Event Stream (fan-out to all engines)
        ↓
┌──────────────┬─────────────────┬──────────────────┐
│ Fraud Engine │  Graph Engine   │  Anomaly Engine  │
│  XGBoost+RF  │  GCN+GAT+TGN   │  IsoForest+AE    │
└──────────────┴─────────────────┴──────────────────┘
        ↓
Risk Aggregator (composite score 0-100)
        ↓
┌─────────────────┬──────────────────────┐
│  Case Manager   │  LLM Investigation   │
│  (FastAPI+PG)   │  (Ollama+LangChain)  │
└─────────────────┴──────────────────────┘
        ↓
Data Layer: TimescaleDB | Neo4j | Redis | ChromaDB
        ↓
Monitoring: MLflow | Evidently | Prometheus | Grafana
```

---

## 🚀 Build Progress

- [x] **Phase 1** — Infrastructure (Docker Compose: 13 services)
- [x] **Phase 2a** — Synthetic data generation (1M transactions, 4 fraud types)
- [ ] **Phase 2b** — ML model training (XGBoost, GCN, Anomaly)
- [ ] **Phase 3** — FastAPI backend (13 modules)
- [ ] **Phase 4** — LLM investigation assistant
- [ ] **Phase 5** — React dashboard

---

## 🛠️ Tech Stack (100% Free & Open Source)

**Backend:** Python 3.11, FastAPI, Celery  
**Databases:** TimescaleDB, Neo4j Community, Redis, ChromaDB  
**Streaming:** Apache Kafka, Apache Flink  
**ML:** PyTorch, XGBoost, scikit-learn, PyTorch Geometric  
**LLM:** Ollama + Llama 3.1 8B (local)  
**RAG:** LangChain, sentence-transformers  
**Monitoring:** MLflow, Evidently AI, Prometheus, Grafana  
**Frontend:** React 18, D3.js, TailwindCSS  
**Infra:** Docker, Docker Compose  

---

## ⚡ Quick Start

### Prerequisites
- Docker Desktop (16GB+ RAM recommended)
- Python 3.11
- Git Bash (Windows)

### 1. Clone and setup
```bash
git clone https://github.com/nite208/upi-fraud-platform.git
cd upi-fraud-platform
cp .env.example .env
# Edit .env with your passwords
```

### 2. Start all 13 services
```bash
docker compose up -d
docker compose ps   # verify all running
```

### 3. Initialize databases
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
pip install psycopg2-binary neo4j python-dotenv
python backend/database/init_db.py
python backend/database/init_neo4j.py
```

### 4. Create Kafka topics
```bash
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.transactions --partitions 8 --replication-factor 1
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.fraud-alerts --partitions 4 --replication-factor 1
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.graph-events --partitions 4 --replication-factor 1
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.dlq --partitions 2 --replication-factor 1
```

### 5. Pull LLM model
```bash
docker exec fraud_ollama ollama pull phi3:mini   # 4GB RAM
# or
docker exec fraud_ollama ollama pull llama3.1:8b  # 8GB+ RAM
```

---

## 📊 Service URLs (after docker compose up)

| Service | URL | Credentials |
|---|---|---|
| FastAPI (Phase 3) | http://localhost:8000 | — |
| Neo4j Browser | http://localhost:7474 | neo4j / fraudpass123 |
| Kafka UI | http://localhost:8080 | — |
| Flink Dashboard | http://localhost:8081 | — |
| MLflow | http://localhost:5000 | — |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | — |
| ChromaDB | http://localhost:8001 | — |
| Ollama | http://localhost:11434 | — |

---

## 📁 Project Structure

```
upi-fraud-platform/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── engines/          # ML fraud/anomaly engines
│   ├── graph/            # Neo4j + GNN models
│   ├── llm/              # LangChain RAG pipeline
│   ├── streaming/        # Kafka consumers
│   ├── monitoring/       # MLflow + Evidently
│   ├── compliance/       # SAR + audit trail
│   └── database/         # Schema + init scripts
├── frontend/             # React dashboard (Phase 5)
├── ml/
│   ├── training/         # Model training scripts
│   ├── models/           # Trained model artifacts
│   └── data/             # Processed feature data
├── data/
│   ├── raw/              # Source data
│   ├── synthetic/        # Generated training data
│   └── processed/        # Feature-engineered datasets
├── notebooks/            # Colab training notebooks
├── docker/               # Dockerfiles + configs
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built step by step — infrastructure → data → ML → API → UI*