import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (AccountGraphResponse, AccountNode,
                             GraphEdge, FraudRing, MuleAccount)
from database.neo4j_client import (get_account_neighbourhood,
                                    get_mule_candidates,
                                    get_shortest_path)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/graph/account/{vpa}", response_model=AccountGraphResponse)
async def get_account_graph(vpa: str):
    data = get_account_neighbourhood(vpa)
    if not data:
        raise HTTPException(status_code=404,
                            detail=f"Account {vpa} not found in graph")

    edges = []
    for e in data.get('sent', []):
        if e.get('target'):
            edges.append(GraphEdge(
                source    = vpa,
                target    = e['target'],
                amount    = float(e.get('amount') or 0),
                timestamp = str(e.get('timestamp') or '')
            ))
    for e in data.get('received', []):
        if e.get('source'):
            edges.append(GraphEdge(
                source    = e['source'],
                target    = vpa,
                amount    = float(e.get('amount') or 0),
                timestamp = str(e.get('timestamp') or '')
            ))

    return AccountGraphResponse(
        node = AccountNode(
            vpa        = vpa,
            risk_score = float(data.get('risk_score') or 0),
            txn_count  = len(edges),
            created_at = None
        ),
        edges          = edges[:50],
        ring_membership = None,
        mule_score     = 0.0
    )


@router.get("/graph/mules", response_model=List[MuleAccount])
async def get_mule_accounts(limit: int = Query(20, le=100)):
    candidates = get_mule_candidates(limit=limit)
    return [
        MuleAccount(
            vpa        = r['vpa'],
            mule_score = round(float(r.get('mule_score', 0)), 3),
            in_degree  = int(r.get('in_degree', 0)),
            out_degree = int(r.get('out_degree', 0)),
            account_age = None
        )
        for r in candidates
    ]


@router.get("/graph/rings", response_model=List[FraudRing])
async def get_fraud_rings(limit: int = Query(10, le=50)):
    """
    Detect fraud rings using Louvain community detection.
    Returns accounts in suspiciously dense clusters.
    """
    from database.neo4j_client import get_driver
    cypher = """
        MATCH (a:Account)-[:SENT_TO]->(b:Account)
        WHERE a.risk_score > 0.5 OR b.risk_score > 0.5
        WITH a, collect(DISTINCT b.vpa) AS neighbours
        WHERE size(neighbours) >= 3
        RETURN a.vpa AS hub,
               neighbours,
               size(neighbours) AS member_count,
               a.risk_score AS score
        ORDER BY member_count DESC
        LIMIT $limit
    """
    try:
        with get_driver().session() as session:
            result = session.run(cypher, limit=limit)
            rings  = []
            for i, r in enumerate(result):
                members = [r['hub']] + list(r['neighbours'])
                rings.append(FraudRing(
                    ring_id      = f"ring_{i+1}",
                    member_count = int(r['member_count']) + 1,
                    score        = float(r.get('score') or 0),
                    members      = members[:20]
                ))
            return rings
    except Exception as e:
        logger.error(f"get_fraud_rings failed: {e}")
        return []


@router.get("/graph/path/{vpa_a}/{vpa_b}")
async def get_path(vpa_a: str, vpa_b: str):
    result = get_shortest_path(vpa_a, vpa_b)
    if not result.get('connected'):
        return {
            "vpa_a":     vpa_a,
            "vpa_b":     vpa_b,
            "connected": False,
            "hops":      -1,
            "path":      []
        }
    return {
        "vpa_a":     vpa_a,
        "vpa_b":     vpa_b,
        "connected": True,
        "hops":      result['hops'],
        "path":      result['path']
    }