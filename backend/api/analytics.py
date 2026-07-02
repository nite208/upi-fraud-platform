import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import ModelMetrics, HeatmapItem
from engines.fraud_engine import get_model_info
from database.timescale import get_conn

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analytics/model/performance", response_model=ModelMetrics)
async def get_model_performance():
    try:
        info = get_model_info()
        return ModelMetrics(
            model_version   = info.get('model_version', '1.0'),
            xgb_pr_auc      = info.get('xgb_pr_auc', 0),
            rf_pr_auc       = info.get('rf_pr_auc', 0),
            ensemble_pr_auc = info.get('ensemble_pr_auc', 0),
            best_f2         = info.get('best_f2', 0),
            best_threshold  = info.get('best_threshold', 0.41),
            features        = info.get('features', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/heatmap", response_model=List[HeatmapItem])
async def get_fraud_heatmap():
    """
    Returns fraud alert distribution.
    In production this groups by GPS region.
    For now returns decision-based summary.
    """
    sql = """
        SELECT fd.decision,
               COUNT(*)        AS alert_count,
               SUM(t.amount)   AS total_amount
        FROM fraud_decisions fd
        JOIN transactions t ON fd.txn_id = t.txn_id
        WHERE fd.decided_at > NOW() - INTERVAL '24 hours'
        GROUP BY fd.decision
        ORDER BY alert_count DESC
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()

        risk_map = {'BLOCK': 'critical', 'REVIEW': 'high', 'SAFE': 'low'}
        return [
            HeatmapItem(
                region       = row[0],
                alert_count  = int(row[1]),
                risk_level   = risk_map.get(row[0], 'low'),
                total_amount = float(row[2] or 0)
            )
            for row in rows
        ]
    except Exception as e:
        logger.error(f"heatmap failed: {e}")
        return []


@router.get("/analytics/drift")
async def get_drift_report():
    """Placeholder — Evidently AI drift reports added in Phase 6."""
    return {
        "drift_detected":    False,
        "features_drifted":  [],
        "max_psi":           0.0,
        "report_date":       datetime.utcnow().isoformat(),
        "note": "Evidently AI drift detection configured in Phase 6"
    }


@router.post("/analytics/retrain/trigger")
async def trigger_retrain(reason: str = "manual"):
    """Trigger model retraining pipeline."""
    import mlflow
    import config
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    try:
        with mlflow.start_run(run_name=f"retrain_{reason}_{datetime.utcnow().date()}"):
            mlflow.log_param("trigger_reason", reason)
            mlflow.log_param("triggered_at", datetime.utcnow().isoformat())
        return {
            "status":       "triggered",
            "reason":       reason,
            "triggered_at": datetime.utcnow().isoformat(),
            "note": "Full retraining pipeline runs in Phase 6"
        }
    except Exception as e:
        return {
            "status":  "queued",
            "reason":  reason,
            "note":    str(e)
        }


@router.get("/analytics/summary")
async def get_summary():
    """Quick stats for dashboard overview cards."""
    sql = """
        SELECT
            COUNT(*)                                          AS total_txns,
            COUNT(*) FILTER (WHERE fd.decision = 'BLOCK')    AS blocked,
            COUNT(*) FILTER (WHERE fd.decision = 'REVIEW')   AS reviews,
            COUNT(*) FILTER (WHERE fd.decision = 'SAFE')     AS safe,
            ROUND(AVG(fd.composite_score)::numeric, 2)       AS avg_score,
            ROUND(SUM(t.amount)::numeric, 2)                 AS total_amount
        FROM fraud_decisions fd
        JOIN transactions t ON fd.txn_id = t.txn_id
        WHERE fd.decided_at > NOW() - INTERVAL '24 hours'
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()
        return {
            "period":       "last_24h",
            "total_txns":   int(row[0] or 0),
            "blocked":      int(row[1] or 0),
            "reviews":      int(row[2] or 0),
            "safe":         int(row[3] or 0),
            "avg_score":    float(row[4] or 0),
            "total_amount": float(row[5] or 0),
            "timestamp":    datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"summary failed: {e}")
        return {"error": str(e)}