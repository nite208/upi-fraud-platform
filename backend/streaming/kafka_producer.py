import json
import logging
from typing import Dict, Any
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)
_producer = None

def get_producer():
    global _producer
    if _producer is None:
        try:
            from kafka import KafkaProducer
            _producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                request_timeout_ms=3000,
                api_version_auto_timeout_ms=3000,
                max_block_ms=3000,
                retries=1
            )
            logger.info("✓ Kafka producer connected")
        except Exception as e:
            logger.warning(f"Kafka producer unavailable: {e}")
            return None
    return _producer

def publish_transaction(txn: Dict[str, Any]) -> bool:
    try:
        producer = get_producer()
        if not producer:
            return False
        producer.send(config.KAFKA_TOPIC_TRANSACTIONS,
                      key=txn.get('txn_id'), value=txn)
        producer.flush(timeout=2)
        return True
    except Exception as e:
        logger.debug(f"Kafka publish skipped: {e}")
        return False

def publish_alert(alert: Dict[str, Any]) -> bool:
    try:
        producer = get_producer()
        if not producer:
            return False
        producer.send(config.KAFKA_TOPIC_ALERTS,
                      key=alert.get('txn_id'), value=alert)
        producer.flush(timeout=2)
        return True
    except Exception as e:
        logger.debug(f"Kafka alert skipped: {e}")
        return False

def publish_graph_event(event: Dict[str, Any]) -> bool:
    try:
        producer = get_producer()
        if not producer:
            return False
        producer.send(config.KAFKA_TOPIC_GRAPH, value=event)
        producer.flush(timeout=2)
        return True
    except Exception as e:
        logger.debug(f"Kafka graph event skipped: {e}")
        return False

def check_connection() -> bool:
    try:
        p = get_producer()
        return p is not None
    except Exception:
        return False