import logging
import re
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

# ── Simple regex-based PII masker ─────────────────────────────────────────────
# Using regex instead of Presidio to avoid heavy NLP model download on 8GB RAM

VPA_PATTERN    = re.compile(r'[a-zA-Z0-9._+-]+@[a-zA-Z0-9]+', re.IGNORECASE)
PHONE_PATTERN  = re.compile(r'(\+91|91)?[6-9]\d{9}')
AMOUNT_PATTERN = re.compile(r'₹?\d{1,3}(,\d{3})*(\.\d{1,2})?')
IP_PATTERN     = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
DEVICE_PATTERN = re.compile(r'device[-_][a-zA-Z0-9-]{4,}', re.IGNORECASE)


def mask_text(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Mask PII in text before sending to LLM.
    Returns masked text and a token map for de-anonymisation.

    Example:
        Input:  "rahul123@okicici sent ₹50,000 to merchant@ybl"
        Output: "[VPA_1] sent [AMOUNT_1] to [VPA_2]"
    """
    token_map = {}
    counter   = {}

    def replace(pattern, label, text):
        def _replace(m):
            val = m.group(0)
            # Check if already tokenised
            for token, original in token_map.items():
                if original == val:
                    return token
            counter[label] = counter.get(label, 0) + 1
            token = f"[{label}_{counter[label]}]"
            token_map[token] = val
            return token
        return pattern.sub(_replace, text)

    text = replace(VPA_PATTERN,    'VPA',    text)
    text = replace(PHONE_PATTERN,  'PHONE',  text)
    text = replace(IP_PATTERN,     'IP',     text)
    text = replace(DEVICE_PATTERN, 'DEVICE', text)

    return text, token_map


def unmask_text(text: str, token_map: Dict[str, str]) -> str:
    """Restore original values from token map."""
    for token, original in token_map.items():
        text = text.replace(token, original)
    return text


def mask_transaction(txn: dict) -> Tuple[dict, Dict[str, str]]:
    """Mask PII fields in a transaction dict."""
    token_map = {}
    masked    = txn.copy()

    def _mask_field(value: str, label: str, idx: int) -> str:
        token = f"[{label}_{idx}]"
        token_map[token] = value
        return token

    if masked.get('sender_vpa'):
        masked['sender_vpa'] = _mask_field(masked['sender_vpa'], 'VPA', 1)
    if masked.get('receiver_vpa'):
        masked['receiver_vpa'] = _mask_field(masked['receiver_vpa'], 'VPA', 2)
    if masked.get('ip_address'):
        masked['ip_address'] = _mask_field(masked['ip_address'], 'IP', 1)
    if masked.get('device_id'):
        masked['device_id'] = _mask_field(masked['device_id'], 'DEVICE', 1)

    return masked, token_map