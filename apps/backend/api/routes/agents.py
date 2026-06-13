"""
Orchestrator router
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.orchestrator import OrchestratorAgent
from utils.guardrails import scan_prompt_for_injection
from typing import Optional

router = APIRouter()
orchestrator = OrchestratorAgent()

@router.post("/chat")
async def chat_orchestrate(
    query: str = Body(..., embed=True),
    file_data: Optional[dict] = Body(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Enforce AI Safety Guardrails input scanning
    if scan_prompt_for_injection(query):
        raise HTTPException(
            status_code=400,
            detail="AI Guardrails: Security policy block. Unsafe input prompt detected (jailbreak/override attempt)."
        )
        
    try:
        result = await orchestrator.route_and_analyze(query, current_user, file_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

