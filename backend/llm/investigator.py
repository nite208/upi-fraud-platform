import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.ollama_client import generate, FRAUD_ANALYST_SYSTEM
from llm.vector_store  import search_similar
from llm.pii_masker    import mask_text
from database.timescale import get_conn

logger = logging.getLogger(__name__)

# ── In-memory session store ───────────────────────────────────────────────────
_sessions: Dict[str, List[Dict]] = {}


def _get_session(session_id: str) -> List[Dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


def _add_to_session(session_id: str, role: str, content: str):
    history = _get_session(session_id)
    history.append({'role': role, 'content': content, 'ts': datetime.utcnow().isoformat()})
    # Keep last 6 turns only
    if len(history) > 12:
        _sessions[session_id] = history[-12:]


def _get_transaction_context(txn_id: str) -> str:
    """Fetch transaction + decision data from TimescaleDB."""
    sql = """
        SELECT t.txn_id, t.sender_vpa_masked, t.receiver_vpa_masked,
               t.amount, t.timestamp, t.upi_app, t.merchant_code,
               fd.composite_score, fd.ml_score, fd.graph_score,
               fd.anomaly_score, fd.decision, fd.shap_values
        FROM transactions t
        LEFT JOIN fraud_decisions fd ON t.txn_id = fd.txn_id
        WHERE t.txn_id = %s
        LIMIT 1
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (txn_id,))
            row = cur.fetchone()
            if not row:
                return ""
            cols = [d[0] for d in cur.description]
            data = dict(zip(cols, row))
            return f"""
Transaction ID: {data['txn_id']}
Sender: {data['sender_vpa_masked']}
Receiver: {data['receiver_vpa_masked']}
Amount: ₹{data['amount']:,.2f}
Timestamp: {data['timestamp']}
UPI App: {data['upi_app']}
Merchant Code: {data.get('merchant_code') or 'None (P2P)'}

Risk Scores:
  Composite Score: {data['composite_score']:.1f}/100
  ML Score: {data['ml_score']:.1f}/100
  Graph Score: {data['graph_score']:.1f}/100
  Anomaly Score: {data['anomaly_score']:.1f}/100
  Decision: {data['decision']}

SHAP Explanations (top features driving the score):
{_format_shap(data.get('shap_values', {}))}
"""
    except Exception as e:
        logger.error(f"_get_transaction_context failed: {e}")
        return ""


def _format_shap(shap_data: Any) -> str:
    if not shap_data:
        return "  Not available"
    try:
        if isinstance(shap_data, str):
            import json
            shap_data = json.loads(shap_data)
        top5 = shap_data.get('top5', [])
        lines = []
        for item in top5[:5]:
            direction = "↑ fraud" if item.get('direction') == 'fraud' else "↓ normal"
            lines.append(f"  {item['feature']}: {item['shap_value']:+.4f} ({direction})")
        return '\n'.join(lines) if lines else "  Not available"
    except Exception:
        return "  Not available"


def _build_rag_context(query: str, txn_context: str) -> str:
    """Retrieve relevant documents from ChromaDB."""
    docs = search_similar(query, n_results=3)
    if not docs:
        return ""
    context_parts = []
    for doc in docs:
        relevance = doc.get('relevance', 0)
        if relevance > 0.3:
            context_parts.append(f"[Reference — relevance {relevance:.2f}]\n{doc['text']}")
    return '\n\n'.join(context_parts)


async def explain_transaction(txn_id: str) -> Dict[str, Any]:
    """Generate a plain-English fraud explanation for a transaction."""
    txn_context = _get_transaction_context(txn_id)
    if not txn_context:
        return {
            'explanation': f"Transaction {txn_id} not found in database.",
            'sources':     [],
            'txn_id':      txn_id
        }

    rag_context = _build_rag_context(
        f"fraud analysis transaction score {txn_context[:200]}", txn_context
    )

    prompt = f"""Analyse this UPI transaction and explain why it was flagged:

{txn_context}

Relevant fraud typologies and guidelines:
{rag_context}

Provide a clear, structured explanation covering:
1. Why this transaction was flagged (cite specific scores and features)
2. What fraud pattern this most resembles
3. What the analyst should investigate next
4. Recommended action (approve / escalate / block)

Keep it under 100 words. Be direct."""

    explanation = await generate(
        prompt     = prompt,
        system     = FRAUD_ANALYST_SYSTEM,
        max_tokens = 500
    )

    docs = search_similar(f"fraud {txn_context[:100]}", n_results=3)
    sources = [d['metadata'].get('fraud_type', d['metadata'].get('type', ''))
               for d in docs]

    return {
        'explanation': explanation,
        'sources':     sources,
        'txn_id':      txn_id
    }


async def answer_question(question: str,
                          txn_id:     Optional[str] = None,
                          case_id:    Optional[str] = None,
                          session_id: Optional[str] = None) -> Dict[str, Any]:
    """Answer an analyst's question with RAG context."""
    if not session_id:
        session_id = str(uuid.uuid4())

    # Mask PII in question
    masked_question, _ = mask_text(question)

    # Get transaction context if provided
    txn_context = ""
    if txn_id:
        txn_context = _get_transaction_context(txn_id)

    # RAG retrieval
    rag_context = _build_rag_context(masked_question, txn_context)

    # Build conversation history
    history = _get_session(session_id)
    history_text = ""
    if history:
        recent = history[-4:]
        history_text = "\n".join([
            f"{h['role'].upper()}: {h['content']}"
            for h in recent
        ])

    # Build full prompt
    prompt_parts = []
    if history_text:
        prompt_parts.append(f"Previous conversation:\n{history_text}\n")
    if txn_context:
        prompt_parts.append(f"Transaction context:\n{txn_context}")
    if rag_context:
        prompt_parts.append(f"Reference knowledge:\n{rag_context}")
    prompt_parts.append(f"Analyst question: {masked_question}")
    prompt_parts.append("Answer concisely and factually:")

    prompt = "\n\n".join(prompt_parts)

    answer = await generate(
        prompt     = prompt,
        system     = FRAUD_ANALYST_SYSTEM,
        max_tokens = 600
    )

    # Update session
    _add_to_session(session_id, 'user',      masked_question)
    _add_to_session(session_id, 'assistant', answer)

    docs    = search_similar(masked_question, n_results=3)
    sources = [d['metadata'].get('type', 'unknown') for d in docs]

    return {
        'answer':     answer,
        'sources':    sources,
        'session_id': session_id,
        'txn_id':     txn_id
    }


async def generate_sar_draft(case_id: str) -> Dict[str, Any]:
    """Generate a Suspicious Activity Report draft."""
    sql = """
        SELECT fc.case_id, fc.txn_id, fc.risk_score, fc.disposition,
               t.sender_vpa_masked, t.receiver_vpa_masked, t.amount,
               t.timestamp, fd.decision, fd.composite_score,
               fd.ml_score, fd.shap_values
        FROM fraud_cases fc
        JOIN transactions t ON fc.txn_id = t.txn_id
        JOIN fraud_decisions fd ON fc.txn_id = fd.txn_id
        WHERE fc.case_id = %s
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (case_id,))
            row = cur.fetchone()
            if not row:
                return {'sar_draft': 'Case not found', 'case_id': case_id}
            cols = [d[0] for d in cur.description]
            data = dict(zip(cols, row))
    except Exception as e:
        return {'sar_draft': f'DB error: {e}', 'case_id': case_id}

    rag_context = _build_rag_context(
        f"suspicious activity report fraud ₹{data['amount']}", ""
    )

    prompt = f"""Generate a Suspicious Activity Report (SAR) for this fraud case.

Case Details:
- Case ID: {data['case_id']}
- Transaction: {data['txn_id']}
- Sender: {data['sender_vpa_masked']}
- Receiver: {data['receiver_vpa_masked']}
- Amount: ₹{data['amount']:,.2f}
- Date/Time: {data['timestamp']}
- Risk Score: {data['composite_score']:.1f}/100
- AI Decision: {data['decision']}

Reference:
{rag_context}

Write a formal SAR with these sections:
1. SUBJECT OF REPORT
2. SUSPICIOUS ACTIVITY DESCRIPTION
3. FRAUD INDICATORS IDENTIFIED
4. RECOMMENDED ACTION
5. REPORTING OFFICER (leave blank for analyst to fill)

Keep it professional and under 300 words."""

    sar = await generate(
        prompt     = prompt,
        system     = FRAUD_ANALYST_SYSTEM,
        temperature = 0.2,
        max_tokens  = 700
    )

    return {
        'sar_draft':         sar,
        'case_id':           case_id,
        'fatf_typology':     'Layering / Account Takeover',
        'rbi_category':      'Unauthorised Electronic Fund Transfer',
        'review_required':   True,
        'generated_at':      datetime.utcnow().isoformat()
    }