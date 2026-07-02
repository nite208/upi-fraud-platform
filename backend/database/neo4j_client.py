import logging
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)
_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        logger.info("✓ Neo4j driver created")
    return _driver

def check_connection() -> bool:
    try:
        get_driver().verify_connectivity()
        return True
    except Exception as e:
        logger.error(f"Neo4j connection failed: {e}")
        return False

# ── Graph operations ──────────────────────────────────────────────────────────
def upsert_transaction_edge(sender_vpa: str, receiver_vpa: str,
                             amount: float, txn_id: str,
                             timestamp: str, is_fraud: bool = False) -> bool:
    cypher = """
        MERGE (s:Account {vpa: $sender})
        ON CREATE SET s.risk_score = 0.0, s.created_at = datetime()
        MERGE (r:Account {vpa: $receiver})
        ON CREATE SET r.risk_score = 0.0, r.created_at = datetime()
        CREATE (s)-[:SENT_TO {
            txn_id: $txn_id,
            amount: $amount,
            timestamp: $timestamp,
            is_fraud: $is_fraud
        }]->(r)
        WITH s
        SET s.txn_count = COALESCE(s.txn_count, 0) + 1
    """
    try:
        with get_driver().session() as session:
            session.run(cypher, sender=sender_vpa, receiver=receiver_vpa,
                        txn_id=txn_id, amount=amount,
                        timestamp=timestamp, is_fraud=is_fraud)
        return True
    except Exception as e:
        logger.error(f"upsert_transaction_edge failed: {e}")
        return False

def get_account_neighbourhood(vpa: str, hops: int = 2) -> Dict[str, Any]:
    cypher = """
        MATCH (a:Account {vpa: $vpa})
        OPTIONAL MATCH (a)-[r:SENT_TO]->(b:Account)
        OPTIONAL MATCH (c:Account)-[r2:SENT_TO]->(a)
        RETURN a,
               collect(DISTINCT {target: b.vpa, amount: r.amount,
                                  timestamp: r.timestamp}) AS sent,
               collect(DISTINCT {source: c.vpa, amount: r2.amount,
                                  timestamp: r2.timestamp}) AS received,
               a.risk_score AS risk_score
        LIMIT 1
    """
    try:
        with get_driver().session() as session:
            result = session.run(cypher, vpa=vpa)
            record = result.single()
            if not record:
                return {}
            return {
                'vpa':       vpa,
                'risk_score': record['risk_score'] or 0.0,
                'sent':      record['sent'],
                'received':  record['received']
            }
    except Exception as e:
        logger.error(f"get_account_neighbourhood failed: {e}")
        return {}

def update_account_risk(vpa: str, risk_score: float) -> bool:
    cypher = """
        MERGE (a:Account {vpa: $vpa})
        SET a.risk_score = $risk_score,
            a.last_updated = datetime()
    """
    try:
        with get_driver().session() as session:
            session.run(cypher, vpa=vpa, risk_score=risk_score)
        return True
    except Exception as e:
        logger.error(f"update_account_risk failed: {e}")
        return False

def get_mule_candidates(limit: int = 20) -> List[Dict]:
    cypher = """
        MATCH (a:Account)
        WHERE a.txn_count > 5
        OPTIONAL MATCH (a)<-[:SENT_TO]-(inbound:Account)
        OPTIONAL MATCH (a)-[:SENT_TO]->(outbound:Account)
        WITH a,
             count(DISTINCT inbound)  AS in_degree,
             count(DISTINCT outbound) AS out_degree
        WHERE in_degree > out_degree * 2
          AND in_degree > 3
        RETURN a.vpa AS vpa,
               in_degree, out_degree,
               a.risk_score AS risk_score,
               (in_degree * 1.0 / (out_degree + 1)) AS mule_score
        ORDER BY mule_score DESC
        LIMIT $limit
    """
    try:
        with get_driver().session() as session:
            result = session.run(cypher, limit=limit)
            return [dict(r) for r in result]
    except Exception as e:
        logger.error(f"get_mule_candidates failed: {e}")
        return []

def get_account_risk_from_graph(vpa: str) -> float:
    cypher = """
        MATCH (a:Account {vpa: $vpa})
        OPTIONAL MATCH (a)<-[:SENT_TO]-(s:Account)
        OPTIONAL MATCH (a)-[:SENT_TO]->(r:Account)
        WITH a,
             avg(s.risk_score) AS avg_sender_risk,
             count(DISTINCT s) AS in_deg,
             count(DISTINCT r) AS out_deg
        RETURN COALESCE(a.risk_score, 0.0) AS own_risk,
               COALESCE(avg_sender_risk, 0.0) AS network_risk,
               in_deg, out_deg
    """
    try:
        with get_driver().session() as session:
            result = session.run(cypher, vpa=vpa)
            record = result.single()
            if not record:
                return 0.0
            own_risk     = float(record['own_risk'])
            network_risk = float(record['network_risk'])
            in_deg       = int(record['in_deg'])
            out_deg      = int(record['out_deg'])
            mule_signal  = min(1.0, in_deg / max(out_deg + 1, 1) / 5.0)
            graph_score  = (own_risk * 0.5 +
                           network_risk * 0.3 +
                           mule_signal * 0.2)
            return min(1.0, graph_score)
    except Exception as e:
        logger.error(f"get_account_risk_from_graph failed: {e}")
        return 0.0

def get_shortest_path(vpa_a: str, vpa_b: str) -> Dict[str, Any]:
    cypher = """
        MATCH path = shortestPath(
            (a:Account {vpa: $vpa_a})-[:SENT_TO*..6]-(b:Account {vpa: $vpa_b})
        )
        RETURN length(path) AS hops,
               [n IN nodes(path) | n.vpa] AS path_nodes
    """
    try:
        with get_driver().session() as session:
            result = session.run(cypher, vpa_a=vpa_a, vpa_b=vpa_b)
            record = result.single()
            if not record:
                return {'hops': -1, 'path': [], 'connected': False}
            return {
                'hops':      record['hops'],
                'path':      record['path_nodes'],
                'connected': True
            }
    except Exception as e:
        logger.error(f"get_shortest_path failed: {e}")
        return {'hops': -1, 'path': [], 'connected': False}