import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)


def aggregate_scores(ml_score: float,
                     graph_score: float,
                     anomaly_score: float) -> Dict[str, Any]:
    composite = (
        ml_score      * config.WEIGHT_ML +
        graph_score   * config.WEIGHT_GRAPH +
        anomaly_score * config.WEIGHT_ANOMALY
    )
    composite = round(min(100.0, max(0.0, composite)), 2)

    if composite <= config.SCORE_SAFE_MAX:
        decision = "SAFE"
    elif composite <= config.SCORE_REVIEW_MAX:
        decision = "REVIEW"
    else:
        decision = "BLOCK"

    now = datetime.utcnow()
    if decision == "BLOCK":
        sla = now + timedelta(minutes=config.SLA_BLOCK_MINUTES)
    elif composite > 60:
        sla = now + timedelta(minutes=config.SLA_HIGH_REVIEW_MINUTES)
    else:
        sla = now + timedelta(minutes=config.SLA_REVIEW_MINUTES)

    create_case = decision in ("BLOCK", "REVIEW") and composite > 40

    return {
        'composite_score': composite,
        'decision':        decision,
        'ml_score':        round(ml_score, 2),
        'graph_score':     round(graph_score, 2),
        'anomaly_score':   round(anomaly_score, 2),
        'sla_deadline':    sla.isoformat(),
        'create_case':     create_case,
        'weights': {
            'ml':      config.WEIGHT_ML,
            'graph':   config.WEIGHT_GRAPH,
            'anomaly': config.WEIGHT_ANOMALY
        }
    }


def apply_hard_rules(result: Dict[str, Any],
                     is_blacklisted: bool = False,
                     velocity_breach: bool = False) -> Dict[str, Any]:
    if is_blacklisted:
        result['decision']        = "BLOCK"
        result['composite_score'] = 100.0
        result['hard_rule']       = "BLACKLIST_MATCH"
        result['create_case']     = True
    elif velocity_breach:
        result['composite_score'] = max(result['composite_score'], 85.0)
        result['decision']        = "BLOCK"
        result['hard_rule']       = "VELOCITY_BREACH"
        result['create_case']     = True
    return result