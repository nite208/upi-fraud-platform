import psycopg2
import psycopg2.pool
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

# ── Connection pool ───────────────────────────────────────────────────────────
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None

def get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            dbname=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        logger.info("✓ TimescaleDB connection pool created")
    return _pool

@contextmanager
def get_conn():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        pool.putconn(conn)

def check_connection() -> bool:
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"TimescaleDB connection failed: {e}")
        return False

# ── Transaction operations ────────────────────────────────────────────────────
def insert_transaction(txn: Dict[str, Any]) -> bool:
    sql = """
        INSERT INTO transactions (
            txn_id, sender_vpa_masked, receiver_vpa_masked,
            amount, timestamp, device_id_hash, ip_hash,
            gps_lat, gps_lng, merchant_code, upi_app, raw_payload
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT DO NOTHING
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (
                txn['txn_id'],
                txn['sender_vpa_masked'],
                txn['receiver_vpa_masked'],
                txn['amount'],
                txn['timestamp'],
                txn.get('device_id_hash'),
                txn.get('ip_hash'),
                txn.get('gps_lat'),
                txn.get('gps_lng'),
                txn.get('merchant_code'),
                txn.get('upi_app'),
                json.dumps(txn.get('raw_payload', {}))
            ))
        return True
    except Exception as e:
        logger.error(f"insert_transaction failed: {e}")
        return False

def insert_decision(decision: Dict[str, Any]) -> bool:
    sql = """
        INSERT INTO fraud_decisions (
            txn_id, composite_score, ml_score, graph_score,
            anomaly_score, decision, model_version, shap_values
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (
                decision['txn_id'],
                decision['composite_score'],
                decision['ml_score'],
                decision['graph_score'],
                decision['anomaly_score'],
                decision['decision'],
                decision.get('model_version', '1.0'),
                json.dumps(decision.get('shap_values', {}))
            ))
        return True
    except Exception as e:
        logger.error(f"insert_decision failed: {e}")
        return False

def create_case(case: Dict[str, Any]) -> Optional[str]:
    sql = """
        INSERT INTO fraud_cases (
            txn_id, risk_score, status,
            assigned_analyst, sla_deadline
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING case_id
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (
                case['txn_id'],
                case['risk_score'],
                case.get('status', 'OPEN'),
                case.get('assigned_analyst'),
                case.get('sla_deadline')
            ))
            row = cur.fetchone()
            return str(row[0]) if row else None
    except Exception as e:
        logger.error(f"create_case failed: {e}")
        return None

def get_cases(status: Optional[str] = None,
              analyst: Optional[str] = None,
              limit: int = 50) -> List[Dict]:
    conditions = []
    params     = []

    if status:
        conditions.append("status = %s")
        params.append(status)
    if analyst:
        conditions.append("assigned_analyst = %s")
        params.append(analyst)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql   = f"""
        SELECT case_id, txn_id, risk_score, status,
               assigned_analyst, sla_deadline, disposition,
               created_at, closed_at
        FROM fraud_cases
        {where}
        ORDER BY risk_score DESC, created_at DESC
        LIMIT %s
    """
    params.append(limit)

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"get_cases failed: {e}")
        return []

def update_case_disposition(case_id: str, disposition: str,
                             notes: str, analyst_id: str) -> bool:
    sql = """
        UPDATE fraud_cases
        SET disposition = %s,
            disposition_notes = %s,
            status = 'CLOSED',
            closed_at = NOW()
        WHERE case_id = %s
    """
    label_sql = """
        INSERT INTO case_labels (case_id, label, analyst_id, notes)
        VALUES (%s, %s, %s, %s)
    """
    action_sql = """
        INSERT INTO analyst_actions (analyst_id, case_id, action_type, details)
        VALUES (%s, %s, %s, %s)
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (disposition, notes, case_id))
            cur.execute(label_sql, (case_id, disposition, analyst_id, notes))
            cur.execute(action_sql, (
                analyst_id, case_id, 'DISPOSITION',
                json.dumps({'disposition': disposition, 'notes': notes})
            ))
        return True
    except Exception as e:
        logger.error(f"update_case_disposition failed: {e}")
        return False

def get_recent_transactions(limit: int = 100,
                             decision: Optional[str] = None) -> List[Dict]:
    conditions = []
    params     = []
    if decision:
        conditions.append("fd.decision = %s")
        params.append(decision)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql   = f"""
        SELECT t.txn_id, t.sender_vpa_masked, t.amount,
               fd.decision, fd.composite_score, t.timestamp
        FROM transactions t
        LEFT JOIN fraud_decisions fd ON t.txn_id = fd.txn_id
        {where}
        ORDER BY t.timestamp DESC
        LIMIT %s
    """
    params.append(limit)
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"get_recent_transactions failed: {e}")
        return []