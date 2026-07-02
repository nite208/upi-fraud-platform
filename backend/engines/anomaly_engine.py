import joblib
import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

_iso_forest = None
_autoencoder = None
_anomaly_scaler = None

# ── Autoencoder definition (must match training) ──────────────────────────────
class FraudAutoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, 16), nn.ReLU(),
            nn.Linear(16, 8), nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16), nn.ReLU(),
            nn.Linear(16, 32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, input_dim)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

def _load_models():
    global _iso_forest, _autoencoder, _anomaly_scaler
    if _iso_forest is None:
        logger.info("Loading anomaly detection models...")
        _iso_forest     = joblib.load(config.ISO_FOREST_PATH)
        _anomaly_scaler = joblib.load(config.ANOMALY_SCALER_PATH)

        _autoencoder = FraudAutoencoder(input_dim=len(config.FEATURES))
        state = torch.load(
            config.AUTOENCODER_PATH,
            map_location=torch.device('cpu'),
            weights_only=True
        )
        _autoencoder.load_state_dict(state)
        _autoencoder.eval()
        logger.info("✓ Anomaly models loaded")

def score_anomaly(features: np.ndarray) -> Dict[str, Any]:
    _load_models()

    # ── Isolation Forest score ─────────────────────────────────────────────
    features_scaled = _anomaly_scaler.transform(features)
    iso_score_raw   = _iso_forest.decision_function(features_scaled)[0]

    # Normalize: lower decision function = more anomalous → flip to 0-1
    iso_score = float(np.clip(1 - (iso_score_raw + 0.5), 0, 1))

    # ── Autoencoder reconstruction error ──────────────────────────────────
    x_tensor = torch.FloatTensor(features_scaled)
    with torch.no_grad():
        recon       = _autoencoder(x_tensor)
        recon_error = float(torch.mean((x_tensor - recon) ** 2).item())

    # Normalize reconstruction error to 0-1 (empirical max ~2.0)
    ae_score = float(np.clip(recon_error / 2.0, 0, 1))

    # ── Ensemble ───────────────────────────────────────────────────────────
    anomaly_score = 0.5 * iso_score + 0.5 * ae_score

    return {
        'anomaly_score':    round(anomaly_score * 100, 2),
        'iso_forest_score': round(iso_score * 100, 2),
        'autoencoder_score': round(ae_score * 100, 2),
        'reconstruction_error': round(recon_error, 6)
    }