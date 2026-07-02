from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ── Enums ─────────────────────────────────────────────────────────────────────
class Decision(str, Enum):
    SAFE   = "SAFE"
    REVIEW = "REVIEW"
    BLOCK  = "BLOCK"

class Disposition(str, Enum):
    TRUE_FRAUD      = "TRUE_FRAUD"
    FALSE_POSITIVE  = "FALSE_POSITIVE"
    INCONCLUSIVE    = "INCONCLUSIVE"

class CaseStatus(str, Enum):
    OPEN        = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED      = "CLOSED"
    ESCALATED   = "ESCALATED"


# ── Transaction schemas ───────────────────────────────────────────────────────
class TransactionRequest(BaseModel):
    txn_id:        Optional[str]   = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_vpa:    str             = Field(..., example="rahul123@okicici")
    receiver_vpa:  str             = Field(..., example="merchant@ybl")
    amount:        float           = Field(..., gt=0, le=100000, example=1500.00)
    timestamp:     Optional[datetime] = None
    device_id:     str             = Field(..., example="device-abc-123")
    ip_address:    str             = Field(..., example="192.168.1.1")
    gps_lat:       Optional[float] = Field(None, example=19.076)
    gps_lng:       Optional[float] = Field(None, example=72.877)
    upi_app:       Optional[str]   = Field("PhonePe", example="PhonePe")
    merchant_code: Optional[str]   = Field(None, example="5411")
    remarks:       Optional[str]   = None

    @validator('sender_vpa', 'receiver_vpa')
    def validate_vpa(cls, v):
        if '@' not in v:
            raise ValueError('VPA must contain @')
        return v.lower().strip()

    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.utcnow()


class ScoreBreakdown(BaseModel):
    ml_score:      float
    graph_score:   float
    anomaly_score: float
    composite:     float

class SHAPValues(BaseModel):
    features:     List[str]
    values:       List[float]
    base_value:   float
    top_features: List[Dict[str, Any]]

class TransactionResponse(BaseModel):
    txn_id:          str
    decision:        Decision
    composite_score: float
    score_breakdown: ScoreBreakdown
    shap_top5:       Optional[List[Dict[str, Any]]] = None
    processing_ms:   float
    timestamp:       datetime
    masked_sender:   str
    status:          str = "queued"

class TransactionListItem(BaseModel):
    txn_id:          str
    sender_vpa:      str
    amount:          float
    decision:        Decision
    composite_score: float
    timestamp:       datetime


# ── Case schemas ──────────────────────────────────────────────────────────────
class CaseResponse(BaseModel):
    case_id:          str
    txn_id:           str
    risk_score:       float
    status:           CaseStatus
    assigned_analyst: Optional[str]
    sla_deadline:     Optional[datetime]
    disposition:      Optional[Disposition]
    created_at:       datetime

class DispositionRequest(BaseModel):
    disposition: Disposition
    notes:       str = Field(..., min_length=10,
                             example="Transaction pattern matches SIM swap fraud")
    analyst_id:  str = Field(..., example="analyst_001")

class CaseNoteRequest(BaseModel):
    content:    str = Field(..., min_length=5)
    analyst_id: str


# ── Graph schemas ─────────────────────────────────────────────────────────────
class AccountNode(BaseModel):
    vpa:         str
    risk_score:  float
    txn_count:   int
    created_at:  Optional[str]

class GraphEdge(BaseModel):
    source:    str
    target:    str
    amount:    float
    timestamp: str

class AccountGraphResponse(BaseModel):
    node:           AccountNode
    edges:          List[GraphEdge]
    ring_membership: Optional[str]
    mule_score:     float

class FraudRing(BaseModel):
    ring_id:      str
    member_count: int
    score:        float
    members:      List[str]

class MuleAccount(BaseModel):
    vpa:          str
    mule_score:   float
    in_degree:    int
    out_degree:   int
    account_age:  Optional[str]


# ── Investigation schemas ─────────────────────────────────────────────────────
class InvestigationRequest(BaseModel):
    question:   str   = Field(..., example="Why was this transaction flagged?")
    txn_id:     Optional[str] = None
    case_id:    Optional[str] = None
    session_id: Optional[str] = None

class InvestigationResponse(BaseModel):
    answer:     str
    sources:    List[str]
    session_id: str
    txn_id:     Optional[str]


# ── Analytics schemas ─────────────────────────────────────────────────────────
class ModelMetrics(BaseModel):
    model_version:  str
    xgb_pr_auc:     float
    rf_pr_auc:      float
    ensemble_pr_auc: float
    best_f2:        float
    best_threshold: float
    features:       List[str]

class HeatmapItem(BaseModel):
    region:      str
    alert_count: int
    risk_level:  str
    total_amount: float


# ── Health schema ─────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status:      str
    timescaledb: str
    neo4j:       str
    redis:       str
    kafka:       str
    ollama:      str
    models:      str
    timestamp:   datetime