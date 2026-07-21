# 🛡️ FraudShield — AI-Powered UPI Fraud Detection & Risk Intelligence Platform

> **India's most advanced open-source UPI fraud intelligence system — combining Machine Learning, Graph Neural Networks, and LLM-powered investigation in one platform.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-PR--AUC%200.9621-orange)](https://xgboost.readthedocs.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-GCN%2BGAT-red?logo=pytorch)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-Llama%203.1%208B%20via%20Groq-yellow)](https://groq.com)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react)](https://react.dev)

---

## 📌 What is FraudShield?

FraudShield is an open-source AI fraud intelligence platform that **automates UPI transaction risk assessment and fraud investigation** for Indian banks and payment service providers.

Right now in every bank, when a suspicious UPI transaction fires an alert, an analyst manually has to:
- Check transaction history and velocity patterns
- Look up receiver account reputation
- Assess graph connections to known fraudsters
- Write a risk assessment and Suspicious Activity Report
- Decide whether to block or approve

**That takes 30–60 minutes per case. FraudShield does it in under 150ms — automatically.**

### How it's different from existing fraud tools

Every existing fraud tool is a **rules engine** — they block transactions above ₹1 lakh or from blacklisted IPs. The analyst still investigates why. FraudShield **automates the investigation itself** using a tri-engine AI system (ML + Graph + Anomaly) plus an LLM investigation assistant. No tool in the Indian UPI ecosystem combines all three layers.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FraudShield Platform                       │
├──────────────────┬──────────────────┬───────────────────────────┤
│   Layer 1        │   Layer 2        │   Layer 3                 │
│   ML Engine      │   Graph Engine   │   Anomaly Engine          │
│                  │                  │                           │
│  XGBoost         │  GCN + GAT       │  Isolation Forest         │
│  Random Forest   │  Neo4j Graph DB  │  PyTorch Autoencoder      │
│  Ensemble 0.9606 │  Fraud Rings     │  Velocity Detection       │
│  SHAP Values     │  Mule Accounts   │  Impossible Travel        │
│  DiCE-ML         │  TGN Temporal    │  Device Fingerprint       │
├──────────────────┴──────────────────┴───────────────────────────┤
│   Layer 4 — Risk Aggregator                                     │
│   ML (40%) + Graph (35%) + Anomaly (25%) → Score 0-100         │
│   Decision: SAFE / REVIEW / BLOCK + SLA timer                  │
├─────────────────────────────────────────────────────────────────┤
│   Layer 5 — LLM Investigation Assistant                         │
│   Groq (Llama 3.1 8B) + LangChain RAG + ChromaDB              │
│   Plain-English fraud explanation + SAR draft generation        │
│   Presidio PII masking before any LLM call                     │
├─────────────────────────────────────────────────────────────────┤
│   Layer 6 — FastAPI Backend (:8000)                            │
│   17 endpoints · Kafka streaming · Redis feature cache         │
│   TimescaleDB audit trail · Case management · WebSocket alerts  │
├─────────────────────────────────────────────────────────────────┤
│   Layer 7 — React Dashboard (:5173)                            │
│   8 pages · Role-based access (Admin/Analyst/Investigator/RM)  │
│   D3.js fraud network · SHAP waterfall · LLM chat interface    │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🤖 Tri-Engine Fraud Detection
- **ML Engine**: XGBoost + Random Forest ensemble trained on 1M synthetic UPI transactions. PR-AUC **0.9621**. SHAP values explain every prediction at feature level.
- **Graph Engine**: GCN + GAT Graph Neural Networks on Neo4j. Detects fraud rings, mule account chains, and network-level patterns invisible to per-transaction analysis.
- **Anomaly Engine**: Isolation Forest + PyTorch Autoencoder trained on normal transactions only. Catches novel fraud patterns without labelled examples.

### 🔍 LLM Investigation Assistant
- Groq-powered Llama 3.1 8B generates plain-English fraud explanations in <3 seconds
- LangChain RAG retrieves similar past cases and RBI fraud typologies from ChromaDB
- Conversational interface: *"Why was this flagged?", "Show similar cases", "Generate SAR draft"*
- Microsoft Presidio masks all PII before any data reaches the LLM

### 📊 Real-Time Streaming Pipeline
- Apache Kafka ingests transactions and fans out to all scoring engines simultaneously
- Redis sliding windows compute velocity features (1m/5m/1h/24h) per sender
- Feast feature store ensures zero training-serving skew
- Target: <150ms end-to-end scoring latency

### 🕸️ Graph Intelligence
- Neo4j persistent account relationship graph
- Louvain community detection identifies fraud ring clusters
- Mule account scoring: high in-degree + low out-degree + new account = mule signal
- D3.js force-directed graph visualisation in dashboard

### 📋 Case Management
- Auto-creates cases for BLOCK/high-risk REVIEW decisions
- SLA timers: BLOCK = 2 hours, High Review = 30 minutes
- Analyst disposition capture → labels feed model retraining pipeline
- Full immutable audit trail in TimescaleDB

### 🔐 Role-Based Access Control
- **Admin**: Full access + user management
- **Risk Manager**: Analytics + model thresholds + settings
- **Fraud Analyst**: Dashboard + cases + LLM investigation
- **Investigator**: Everything + graph network + SAR generation

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API Server | FastAPI + Uvicorn | Async, automatic OpenAPI docs |
| Primary DB | TimescaleDB (PostgreSQL) | Time-series superpowers, 10-100x faster range queries |
| Graph DB | Neo4j Community | Persistent fraud graph, Cypher queries |
| Cache | Redis 7 | Sub-millisecond feature lookups, blacklist O(1) |
| Streaming | Apache Kafka + Flink | Event ingestion + windowed aggregations |
| ML Models | XGBoost, scikit-learn | Tabular fraud detection, PR-AUC 0.9621 |
| Graph ML | PyTorch Geometric | GCN + GAT node embeddings |
| Anomaly | Isolation Forest + PyTorch | Unsupervised anomaly detection |
| LLM Inference | Groq (Llama 3.1 8B) | Fastest free inference, 14,400 req/day |
| RAG | LangChain + ChromaDB | Retrieval-augmented fraud investigation |
| PII Masking | Microsoft Presidio | UPI IDs, phones masked before LLM |
| Explainability | SHAP + DiCE-ML | Feature importance + counterfactuals |
| Synthetic Data | SDV + CTGAN + Faker | 1M realistic UPI transactions |
| Experiment Tracking | MLflow (self-hosted) | Model versioning + champion-challenger |
| Monitoring | Prometheus + Grafana | Latency, alert rates, model drift |
| Frontend | React 18 + Vite + TypeScript | Modern, fast, type-safe |
| Router | TanStack Router | File-based type-safe routing |
| Charts | Recharts + D3.js | Score distribution + fraud network graph |
| Styling | TailwindCSS + Radix UI | UPI blue/orange theme, accessible |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11
- Node.js 20+
- Docker Desktop (16GB RAM recommended, 8GB minimum)
- Git Bash (Windows)

### 1. Clone the repo
```bash
git clone https://github.com/nite208/upi-fraud-platform.git
cd upi-fraud-platform
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in your values:
```
```env
POSTGRES_DB=frauddb
POSTGRES_USER=frauduser
POSTGRES_PASSWORD=your_password
NEO4J_AUTH=neo4j/your_password
GROQ_API_KEY=your_groq_key        # free at console.groq.com
SECRET_KEY=your_secret_key
GF_SECURITY_ADMIN_PASSWORD=admin123
```

### 3. Start infrastructure
```bash
# Pull and start all 13 Docker services
docker compose pull
docker compose up -d

# Verify all services running
docker compose ps
```

### 4. Initialize databases
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Mac/Linux

pip install psycopg2-binary neo4j python-dotenv
python backend/database/init_db.py
python backend/database/init_neo4j.py
```

### 5. Create Kafka topics
```bash
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.transactions --partitions 8 --replication-factor 1
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.fraud-alerts --partitions 4 --replication-factor 1
docker exec fraud_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic upi.dlq --partitions 2 --replication-factor 1
```

### 6. Start backend
```bash
pip install -r requirements.txt
python backend/main.py
# API at http://localhost:8000
# Swagger at http://localhost:8000/docs
```

### 7. Start frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

### 8. Score your first transaction
```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender_vpa": "rahul123@okicici",
    "receiver_vpa": "unknown@ybl",
    "amount": 95000,
    "device_id": "new-device-xyz",
    "ip_address": "192.168.1.1",
    "upi_app": "PhonePe"
  }'
```

---

## 📡 API Reference

### Transactions
```
POST  /api/v1/transactions              — Score a UPI transaction (returns decision + SHAP + score breakdown)
GET   /api/v1/transactions              — List recent transactions with filters
GET   /api/v1/transactions/{txn_id}     — Get single transaction details
```

### Cases
```
GET   /api/v1/cases                     — List cases (filter by status, analyst)
GET   /api/v1/cases/{case_id}           — Get case with full evidence
PATCH /api/v1/cases/{case_id}/disposition — Submit analyst verdict
POST  /api/v1/cases/{case_id}/notes    — Add investigation note
GET   /api/v1/cases/{case_id}/similar  — Semantic similar case search via ChromaDB
```

### LLM Investigation
```
POST  /api/v1/investigate/ask           — Conversational fraud Q&A
POST  /api/v1/investigate/explain/{id} — Plain-English fraud explanation
POST  /api/v1/investigate/sar/{id}     — Generate SAR draft
GET   /api/v1/investigate/sessions/{id} — Get conversation history
```

### Graph
```
GET   /api/v1/graph/account/{vpa}       — Account neighbourhood + risk score
GET   /api/v1/graph/mules               — Mule account candidates
GET   /api/v1/graph/rings               — Detected fraud rings
GET   /api/v1/graph/path/{vpa_a}/{vpa_b} — Shortest path between accounts
```

### Analytics
```
GET   /api/v1/analytics/model/performance — XGB/RF/Ensemble PR-AUC, F2, threshold
GET   /api/v1/analytics/summary           — Dashboard KPIs (24h window)
GET   /api/v1/analytics/heatmap           — Fraud distribution by decision type
POST  /api/v1/analytics/retrain/trigger   — Trigger model retraining
GET   /health                             — Full service health check
```

---

## 🧪 Test Cases

Run these to verify the full pipeline:

| # | Test | Command | Expected |
|---|------|---------|----------|
| 1 | High-risk transaction | POST /transactions with amount=95000, new device | Score >70, REVIEW/BLOCK decision |
| 2 | Normal transaction | POST /transactions with amount=500, known receiver | Score <30, SAFE decision |
| 3 | Velocity attack | POST 10 transactions in 60s from same VPA | Escalating scores, BLOCK |
| 4 | LLM explanation | POST /investigate/explain/{txn_id} | Plain-English fraud analysis |
| 5 | Case creation | GET /cases after a BLOCK decision | Case auto-created with SLA |
| 6 | Disposition | PATCH /cases/{id}/disposition | Label stored, case closed |
| 7 | Graph mules | GET /graph/mules | List of high in-degree accounts |
| 8 | Model metrics | GET /analytics/model/performance | PR-AUC 0.9621 confirmed |

---

## 🗄️ Infrastructure

### Docker Services (13 total)

| Service | Port | Purpose |
|---------|------|---------|
| TimescaleDB | 5432 | Primary time-series database |
| Neo4j | 7474, 7687 | Account relationship graph |
| Redis | 6379 | Feature cache + blacklist |
| Kafka | 29092 | Event streaming backbone |
| Zookeeper | 2181 | Kafka coordination |
| Kafka UI | 8080 | Visual topic monitor |
| Flink JobManager | 8081 | Stream processing |
| MLflow | 5000 | Experiment tracking |
| ChromaDB | 8001 | Vector store for RAG |
| Ollama | 11434 | Local LLM (optional, Groq recommended) |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Monitoring dashboards |

### Minimum for Demo (8GB RAM)
```bash
docker start fraud_timescaledb fraud_redis fraud_chromadb fraud_kafka fraud_zookeeper
```

---

## 🤖 ML Models

All models trained on **Google Colab free T4 GPU** on 1,048,575 synthetic UPI transactions:

| Model | Type | Metric | Value |
|-------|------|--------|-------|
| XGBoost | Supervised | PR-AUC | **0.9621** |
| Random Forest | Supervised | PR-AUC | **0.9555** |
| Ensemble (XGB+RF) | Supervised | PR-AUC | **0.9606** |
| Ensemble | Supervised | F2-Score | **0.9553** |
| Isolation Forest | Unsupervised | PR-AUC | 0.5795 |
| Autoencoder | Semi-supervised | PR-AUC | 0.7109 |
| GCN+GAT | Graph | Node embeddings | 73k × 128 |

**Fraud types in training data:**
- Velocity attack (rapid micro-transfers)
- Account takeover (new device + new IP)
- Mule chain (layered money laundering)
- Large unusual transfer (amount anomaly)

---

## 📁 Project Structure

```
upi-fraud-platform/
├── backend/
│   ├── main.py                    ← FastAPI app + lifespan
│   ├── config.py                  ← Settings from .env
│   ├── api/
│   │   ├── transactions.py        ← Fraud scoring endpoint
│   │   ├── cases.py               ← Case management
│   │   ├── graph.py               ← Neo4j graph endpoints
│   │   ├── analytics.py           ← Model metrics + heatmap
│   │   └── investigate.py         ← LLM investigation
│   ├── engines/
│   │   ├── fraud_engine.py        ← XGBoost+RF + SHAP
│   │   ├── anomaly_engine.py      ← IsoForest + Autoencoder
│   │   └── risk_aggregator.py     ← Score fusion + routing
│   ├── database/
│   │   ├── schema.sql             ← TimescaleDB schema (5 tables)
│   │   ├── init_db.py             ← Schema initializer
│   │   ├── timescale.py           ← Connection pool + CRUD
│   │   └── neo4j_client.py        ← Graph operations
│   ├── llm/
│   │   ├── ollama_client.py       ← Groq API client
│   │   ├── vector_store.py        ← ChromaDB + fraud typologies
│   │   ├── investigator.py        ← RAG pipeline + SAR
│   │   └── pii_masker.py         ← Presidio masking
│   └── streaming/
│       └── kafka_producer.py      ← Kafka event publishing
├── frontend/                      ← React 18 + TanStack Router
│   └── src/routes/
│       ├── index.tsx              ← Landing page
│       ├── login.tsx              ← 4-role authentication
│       ├── dashboard.tsx          ← Main ops dashboard
│       ├── cases.index.tsx        ← Case queue + SLA
│       ├── cases.$id.tsx          ← Case detail + SHAP
│       ├── graph.tsx              ← D3.js fraud network
│       ├── analytics.tsx          ← Model performance charts
│       ├── investigate.tsx        ← LLM chat interface
│       ├── admin.tsx              ← User management
│       └── settings.tsx           ← Thresholds + model health
├── ml/
│   └── models/                    ← Trained model artifacts
│       ├── xgb_fraud_model.pkl
│       ├── rf_fraud_model.pkl
│       ├── feature_scaler.pkl
│       ├── model_metadata.json
│       ├── isolation_forest.pkl
│       ├── autoencoder.pt
│       ├── gcn_model.pt
│       └── node_embeddings.npy
├── notebooks/                     ← Google Colab training notebooks
│   ├── 01_synthetic_data.ipynb
│   ├── 02_fraud_model_training.ipynb
│   ├── 03_anomaly_detection.ipynb
│   └── 04_graph_neural_network.ipynb
├── data/
│   └── synthetic/                 ← 1M generated UPI transactions
├── docker/
│   └── prometheus.yml
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔮 Roadmap

### v1.1 — Production Hardening
- [ ] Real UPI dataset integration (RBI anonymised or partner bank data)
- [ ] Evidently AI drift detection with weekly reports
- [ ] Champion-challenger model testing on shadow traffic
- [ ] WebSocket live alert push to dashboard

### v1.2 — Intelligence Enhancements
- [ ] Flower federated learning — multi-bank collaborative training without data sharing
- [ ] Temporal Graph Networks — detect slow-burn layered laundering
- [ ] Heterogeneous graph (HGT) — account + device + IP + merchant nodes
- [ ] LSTM sequence model for transaction pattern detection

### v2.0 — Enterprise Features
- [ ] RBI FMR report auto-generation
- [ ] Multi-tenant bank isolation
- [ ] JWT auth + RBAC backend enforcement
- [ ] Air-gap mode — Ollama replaces Groq for on-premise deployment
- [ ] Kafka + Flink full streaming pipeline activation

---

## 💡 Why This Matters

> FraudShield is not competing with commercial fraud tools. It is open-sourcing the intelligence layer that Indian fintechs cannot afford.

Commercial UPI fraud platforms cost ₹50L–₹5Cr per year and require dedicated ML teams. Every cooperative bank, NBFC, and payment aggregator in India that processes UPI but cannot afford enterprise tools — that is FraudShield's market.

The architecture is production-ready: swap Groq for Ollama and it runs completely air-gapped. That is the enterprise path.

---

## 👨‍💻 Developer

**Nitesh Kumawat**
- 🎓 Computer Engineering (Honours in Data Science), ISBM College of Engineering, Pune — 2026
- 🏆 Oracle Certified Generative AI Professional
- 🌐 Google Student Ambassador — AI/Gemini
- 💼 [LinkedIn](https://linkedin.com/in/nitesh-kumawat-185356289)
- 🐙 [GitHub](https://github.com/nite208)
- 📧 niteshkumawat2331@gmail.com

---

## 🤝 Contributing

Contributions welcome. Areas actively looking for contributors:
- Real UPI/payment fraud dataset integration
- Better graph anomaly detection algorithms
- Additional fraud typology documents for RAG knowledge base
- UI/UX improvements and accessibility
- RBI compliance report templates

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

> ⭐ If FraudShield helped you or you find it interesting, give it a star — it helps others discover it.
