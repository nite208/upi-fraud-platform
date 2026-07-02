import time
import hashlib
import logging
import redis
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models.schemas import (TransactionRequest, TransactionResponse,
                             TransactionListItem, ScoreBreakdown)
from engines.fraud_engine   import score_transaction
from engines.anomaly_engine import score_anomaly
from engines.risk_aggregator import aggregate_scores, apply_hard_rules
from database.timescale     import (insert_transaction, insert_decision,
                                     create_case, get_recent_transactions)
from database.neo4j_client  import (upsert_transaction_edge,
                                     get_account_risk_from_graph)
from streaming.kafka_producer import publish_transaction, publish_alert

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Redis client ──────────────────────────────────────────────────────────────
def get_redis():
    try:
        r = redis.from_url(config.REDIS_URL, decode_responses=True)
        r.ping()
        return r
    except Exception:
        return None

def mask_vpa(vpa: str) -> str:
    parts = vpa.split('@')
    if len(parts) == 2:
        name = parts[0]
        masked = name[:2] + '*' * max(0, len(name)-2)
        return f"{masked}@{parts[1]}"
    return vpa[:3] + '***'

def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]

def check_blacklist(r, vpa: str, ip: str, device_id: str) -> bool:
    if not r:
        return False
    try:
        return (r.sismember('blacklist:vpa', vpa) or
                r.sismember('blacklist:ip', ip) or
                r.sismember('blacklist:device', device_id))
    except Exception:
        return False

def check_duplicate(r, txn_id: str) -> bool:
    if not r:
        return False
    try:
        key = f"txn:seen:{txn_id}"
        return not r.set(key, 1, nx=True, ex=300)
    except Exception:
        return False

def get_sender_stats(r, sender_vpa: str, amount: float) -> dict:
    if not r:
        return {}
    try:
        key_prefix = f"sender:{hash_value(sender_vpa)}"
        pipe = r.pipeline()
        pipe.incr(f"{key_prefix}:txn_count_1h")
        pipe.expire(f"{key_prefix}:txn_count_1h", 3600)
        pipe.get(f"{key_prefix}:avg_amount")
        results = pipe.execute()

        txn_count = int(results[0])
        avg_amt   = float(results[2]) if results[2] else amount

        # Update rolling average
        new_avg = (avg_amt * (txn_count - 1) + amount) / txn_count
        r.setex(f"{key_prefix}:avg_amount", 3600, new_avg)

        return {
            'txn_count_1h':    txn_count,
            'avg_amount':      new_avg,
            'is_new_receiver': 1,
            'device_shared':   0,
            'receiver_count':  1,
            'device_vpa_count': 1
        }
    except Exception:
        return {}

def background_graph_update(sender: str, receiver: str,
                             amount: float, txn_id: str,
                             timestamp: str, is_fraud: bool):
    try:
        upsert_transaction_edge(sender, receiver, amount,
                                txn_id, timestamp, is_fraud)
    except Exception as e:
        logger.warning(f"Graph update failed: {e}")

# ── Main endpoint ─────────────────────────────────────────────────────────────
@router.post("/transactions", response_model=TransactionResponse, status_code=202)
async def ingest_transaction(txn: TransactionRequest,
                             background: BackgroundTasks):
    t_start = time.time()

    r = get_redis()

    # ── Duplicate check ────────────────────────────────────────────────────
    if check_duplicate(r, txn.txn_id):
        raise HTTPException(status_code=409,
                            detail=f"Duplicate transaction: {txn.txn_id}")

    # ── Blacklist check ────────────────────────────────────────────────────
    is_blacklisted = check_blacklist(r, txn.sender_vpa,
                                     txn.ip_address, txn.device_id)

    # ── Mask PII ───────────────────────────────────────────────────────────
    sender_masked   = mask_vpa(txn.sender_vpa)
    receiver_masked = mask_vpa(txn.receiver_vpa)
    device_hash     = hash_value(txn.device_id)
    ip_hash         = hash_value(txn.ip_address)

    # ── Get velocity features ──────────────────────────────────────────────
    sender_stats = get_sender_stats(r, txn.sender_vpa, txn.amount)

    # ── ML scoring ────────────────────────────────────────────────────────
    txn_dict = txn.dict()
    ml_result = score_transaction(txn_dict, sender_stats, compute_shap=True)
    ml_score  = ml_result['ml_score']

    # ── Graph scoring ──────────────────────────────────────────────────────
    try:
        graph_risk   = get_account_risk_from_graph(txn.sender_vpa)
        graph_score  = round(graph_risk * 100, 2)
    except Exception:
        graph_score = ml_score * 0.5

    # ── Anomaly scoring ────────────────────────────────────────────────────
    import numpy as np
    from engines.fraud_engine import extract_features
    features = extract_features(txn_dict, sender_stats)
    try:
        anomaly_result = score_anomaly(features)
        anomaly_score  = anomaly_result['anomaly_score']
    except Exception:
        anomaly_score = ml_score * 0.3

    # ── Risk aggregation ───────────────────────────────────────────────────
    result = aggregate_scores(ml_score, graph_score, anomaly_score)
    result = apply_hard_rules(result, is_blacklisted=is_blacklisted)

    composite = result['composite_score']
    decision  = result['decision']

    # ── Persist transaction ────────────────────────────────────────────────
    txn_record = {
        'txn_id':             txn.txn_id,
        'sender_vpa_masked':  sender_masked,
        'receiver_vpa_masked': receiver_masked,
        'amount':             txn.amount,
        'timestamp':          txn.timestamp.isoformat(),
        'device_id_hash':     device_hash,
        'ip_hash':            ip_hash,
        'gps_lat':            txn.gps_lat,
        'gps_lng':            txn.gps_lng,
        'merchant_code':      txn.merchant_code,
        'upi_app':            txn.upi_app,
        'raw_payload':        {}
    }
    insert_transaction(txn_record)

    # ── Persist decision ───────────────────────────────────────────────────
    decision_record = {
        'txn_id':          txn.txn_id,
        'composite_score': composite,
        'ml_score':        ml_score,
        'graph_score':     graph_score,
        'anomaly_score':   anomaly_score,
        'decision':        decision,
        'model_version':   ml_result.get('model_version', '1.0'),
        'shap_values':     {'top5': ml_result.get('shap_top5', [])}
    }
    insert_decision(decision_record)

    # ── Create case if needed ──────────────────────────────────────────────
    if result.get('create_case'):
        from datetime import datetime as dt
        sla = dt.fromisoformat(result['sla_deadline'])
        create_case({
            'txn_id':     txn.txn_id,
            'risk_score': composite,
            'status':     'OPEN',
            'sla_deadline': sla
        })

    # ── Publish to Kafka (background) ─────────────────────────────────────
    background.add_task(publish_transaction, txn_record)
    if decision in ("BLOCK", "REVIEW"):
        alert = {**result, 'txn_id': txn.txn_id,
                 'amount': txn.amount, 'sender': sender_masked}
        background.add_task(publish_alert, alert)

    # ── Update graph (background) ──────────────────────────────────────────
    background.add_task(
        background_graph_update,
        txn.sender_vpa, txn.receiver_vpa,
        txn.amount, txn.txn_id,
        txn.timestamp.isoformat(),
        decision == "BLOCK"
    )

    processing_ms = round((time.time() - t_start) * 1000, 2)

    return TransactionResponse(
        txn_id          = txn.txn_id,
        decision        = decision,
        composite_score = composite,
        score_breakdown = ScoreBreakdown(
            ml_score      = ml_score,
            graph_score   = graph_score,
            anomaly_score = anomaly_score,
            composite     = composite
        ),
        shap_top5       = ml_result.get('shap_top5'),
        processing_ms   = processing_ms,
        timestamp       = txn.timestamp,
        masked_sender   = sender_masked,
        status          = "queued"
    )

@router.get("/transactions", response_model=List[TransactionListItem])
async def list_transactions(
    limit:    int            = Query(50, le=200),
    decision: Optional[str] = Query(None)
):
    rows = get_recent_transactions(limit=limit, decision=decision)
    return [
        TransactionListItem(
            txn_id          = r['txn_id'],
            sender_vpa      = r.get('sender_vpa_masked', '***'),
            amount          = float(r.get('amount', 0)),
            decision        = r.get('decision', 'SAFE'),
            composite_score = float(r.get('composite_score', 0)),
            timestamp       = r.get('timestamp', datetime.utcnow())
        )
        for r in rows
    ]

@router.get("/transactions/{txn_id}")
async def get_transaction(txn_id: str):
    rows = get_recent_transactions(limit=1000)
    for r in rows:
        if r['txn_id'] == txn_id:
            return r
    raise HTTPException(status_code=404, detail="Transaction not found")