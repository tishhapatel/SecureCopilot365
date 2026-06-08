"""
Audit Readiness route
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.audit_agent import AuditReadinessAgent
from db import crud, schemas
import json

router = APIRouter()
audit_agent = AuditReadinessAgent()

@router.post("/evaluate")
async def evaluate_audit(
    audit_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        analysis = await audit_agent.analyze(audit_data, current_user)
        
        audit_schema = schemas.AuditReadinessCreate(
            framework=analysis.get("framework", "ISO27001"),
            overall_score=float(analysis.get("overall_readiness_score", 0)),
            controls_total=int(analysis.get("controls_summary", {}).get("total", 93)),
            controls_evidenced=int(analysis.get("controls_summary", {}).get("evidenced", 0)),
            controls_partial=int(analysis.get("controls_summary", {}).get("partial", 0)),
            controls_missing=int(analysis.get("controls_summary", {}).get("missing", 0)),
            critical_gaps=json.dumps(analysis.get("critical_gaps", [])),
            evidence_package=json.dumps(analysis.get("collected_evidence", [])),
            assessed_by=current_user.get("entra_id")
        )
        crud.create_audit_readiness(db, audit_schema)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def list_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.get_audit_readiness(db)
