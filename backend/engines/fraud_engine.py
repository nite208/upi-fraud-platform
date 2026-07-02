import joblib
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

# ── Lazy model loading ────────────────────────────────────────────────────────
_xgb_model     = None
_rf_model      = None
_scaler        = None
_metadata      = None

def _load_models():
    global _xgb_model, _rf_model, _scaler, _metadata
    if _xgb_model is None:
        logger.info("Loading fraud detection models...")
        _xgb_model = joblib.load(config.XGB_MODEL_PATH)
        _rf_model  = joblib.load(config.RF_MODEL_PATH)
        _scaler    = joblib.load(config.FEATURE_SCALER_PATH)
        with open(config.MODEL_METADATA_PATH) as f:
            _metadata = json.load(f)
        logger.info(f"✓ Models loaded | XGB PR-AUC: {_metadata['xgb_pr_auc']:.4f}")

def models_loaded() -> bool:
    return _xgb_model is not None

# ── Feature extraction ────────────────────────────────────────────────────────
def extract_features(txn: Dict[str, Any],
                     sender_stats: Optional[Dict] = None) -> np.ndarray:
    ts = txn.get('timestamp', datetime.utcnow())
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)

    hour       = ts.hour
    dow        = ts.weekday()
    is_weekend = int(dow >= 5)
    is_night   = int(hour < 6 or hour > 22)
    amount     = float(txn.get('amount', 0))
    amount_log = np.log1p(amount)

    upi_app         = txn.get('upi_app', 'PhonePe')
    upi_app_encoded = config.UPI_APP_MAP.get(upi_app, 0)
    has_merchant    = int(txn.get('merchant_code') is not None)
    is_round        = int(amount % 100 == 0)

    # Velocity features from Redis (or defaults)
    s = sender_stats or {}
    sender_txn_count = float(s.get('txn_count_1h', 1))
    sender_avg_amt   = float(s.get('avg_amount', amount))
    amount_vs_avg    = amount / (sender_avg_amt + 1)
    is_new_receiver  = int(s.get('is_new_receiver', 1))
    device_shared    = int(s.get('device_shared', 0))
    receiver_count   = float(s.get('receiver_count', 1))
    device_vpa_count = float(s.get('device_vpa_count', 1))

    features = np.array([[
        amount, amount_log, hour, dow,
        is_weekend, is_night, is_round,
        has_merchant, upi_app_encoded,
        sender_txn_count, sender_avg_amt, amount_vs_avg,
        is_new_receiver, device_shared, receiver_count,
        device_vpa_count
    ]], dtype=np.float32)

    return features

def compute_shap_top5(features: np.ndarray) -> List[Dict[str, Any]]:
    try:
        import shap
        explainer   = shap.TreeExplainer(_xgb_model)
        shap_values = explainer.shap_values(features)[0]
        pairs = list(zip(config.FEATURES, shap_values))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        return [
            {'feature': f, 'shap_value': round(float(v), 4),
             'direction': 'fraud' if v > 0 else 'normal'}
            for f, v in pairs[:5]
        ]
    except Exception as e:
        logger.warning(f"SHAP computation failed: {e}")
        return []

# ── Main scoring function ─────────────────────────────────────────────────────
def score_transaction(txn: Dict[str, Any],
                      sender_stats: Optional[Dict] = None,
                      compute_shap: bool = True) -> Dict[str, Any]:
    _load_models()

    features      = extract_features(txn, sender_stats)
    best_threshold = _metadata.get('best_threshold', 0.41)

    # XGBoost score
    xgb_proba = float(_xgb_model.predict_proba(features)[0][1])

    # Random Forest score
    rf_proba  = float(_rf_model.predict_proba(features)[0][1])

    # Weighted ensemble
    ensemble_proba = 0.6 * xgb_proba + 0.4 * rf_proba

    # Convert to 0-100 scale
    ml_score = round(ensemble_proba * 100, 2)

    # SHAP explanations
    shap_top5 = []
    if compute_shap:
        shap_top5 = compute_shap_top5(features)

    return {
        'ml_score':   ml_score,
        'xgb_proba':  xgb_proba,
        'rf_proba':   rf_proba,
        'ensemble_proba': ensemble_proba,
        'threshold':  best_threshold,
        'shap_top5':  shap_top5,
        'features':   features.tolist()[0],
        'model_version': '1.0'
    }

def get_model_info() -> Dict[str, Any]:
    _load_models()
    return {
        'model_version':   '1.0',
        'xgb_pr_auc':      _metadata.get('xgb_pr_auc'),
        'rf_pr_auc':       _metadata.get('rf_pr_auc'),
        'ensemble_pr_auc': _metadata.get('ensemble_pr_auc'),
        'best_f2':         _metadata.get('best_f2'),
        'best_threshold':  _metadata.get('best_threshold'),
        'features':        config.FEATURES
    }