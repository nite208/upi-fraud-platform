import joblib
import logging
import numpy as np
from typing import Dict, Any
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

_iso_forest = None
_anomaly_scaler = None


def _load_models():
    global _iso_forest, _anomaly_scaler
    if _iso_forest is None:
        logger.info("Loading anomaly detection models (lite mode — no torch)...")
        try:
            _iso_forest     = joblib.load(config.ISO_FOREST_PATH)
            _anomaly_scaler = joblib.load(config.ANOMALY_SCALER_PATH)
            logger.info("✓ Anomaly models loaded (Isolation Forest only)")
        except Exception as e:
            logger.warning(f"Could not load anomaly models: {e} — using fallback scoring")
            _iso_forest = None


def score_anomaly(features: np.ndarray) -> Dict[str, Any]:
    _load_models()

    if _iso_forest is None or _anomaly_scaler is None:
        # Fallback: rule-based anomaly score from raw features
        # features shape: (1, N) — use simple heuristics
        try:
            amount = float(features[0][0]) if features.shape[1] > 0 else 0
            txn_count = float(features[0][3]) if features.shape[1] > 3 else 1
            # High amount or high velocity = higher anomaly
            amount_score = min(amount / 100000.0, 1.0)
            velocity_score = min(txn_count / 20.0, 1.0)
            anomaly_score = (amount_score * 0.6 + velocity_score * 0.4)
        except Exception:
            anomaly_score = 0.1
        return {
            'anomaly_score':     round(anomaly_score * 100, 2),
            'iso_forest_score':  round(anomaly_score * 100, 2),
            'autoencoder_score': 0.0,
            'reconstruction_error': 0.0,
            'mode': 'fallback'
        }

    # ── Isolation Forest score ─────────────────────────────────────────────
    try:
        features_scaled = _anomaly_scaler.transform(features)
        iso_score_raw   = _iso_forest.decision_function(features_scaled)[0]
        iso_score       = float(np.clip(1 - (iso_score_raw + 0.5), 0, 1))
    except Exception as e:
        logger.warning(f"Isolation Forest scoring failed: {e}")
        iso_score = 0.1

    # Autoencoder disabled in lite mode — saves ~1.5GB RAM on 8GB machines
    ae_score = iso_score * 0.8  # approximate from iso score

    anomaly_score = 0.6 * iso_score + 0.4 * ae_score

    return {
        'anomaly_score':     round(anomaly_score * 100, 2),
        'iso_forest_score':  round(iso_score * 100, 2),
        'autoencoder_score': round(ae_score * 100, 2),
        'reconstruction_error': 0.0,
        'mode': 'lite'
    }