import logging
from fastapi import APIRouter, HTTPException
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import InvestigationRequest, InvestigationResponse
from llm.investigator import (explain_transaction, answer_question,
                               generate_sar_draft)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/investigate/ask", response_model=InvestigationResponse)
async def ask_question(body: InvestigationRequest):
    """Ask the LLM assistant a question about a transaction or case."""
    try:
        result = await answer_question(
            question   = body.question,
            txn_id     = body.txn_id,
            case_id    = body.case_id,
            session_id = body.session_id
        )
        return InvestigationResponse(
            answer     = result['answer'],
            sources    = result['sources'],
            session_id = result['session_id'],
            txn_id     = result.get('txn_id')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investigate/explain/{txn_id}")
async def explain_txn(txn_id: str):
    """Generate plain-English fraud explanation for a transaction."""
    try:
        result = await explain_transaction(txn_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investigate/sar/{case_id}")
async def generate_sar(case_id: str):
    """Generate Suspicious Activity Report draft for a case."""
    try:
        result = await generate_sar_draft(case_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/investigate/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for an investigation session."""
    from llm.investigator import _sessions
    history = _sessions.get(session_id, [])
    if not history:
        raise HTTPException(status_code=404,
                            detail="Session not found or expired")
    return {
        "session_id": session_id,
        "messages":   history,
        "turn_count": len(history) // 2
    }