"""
Audit Readiness route
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_with_permission
from agents.audit_agent import AuditReadinessAgent
from db import crud, schemas, models
from auth import permissions
import json

router = APIRouter()
audit_agent = AuditReadinessAgent()

@router.post("/evaluate")
async def evaluate_audit(
    audit_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.RUN_AUDITS))
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
        crud.create_audit_readiness(db, audit_schema, tenant_id=current_user.get("tenant_id"))

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def list_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.VIEW_AUDITS))
):
    return crud.get_audit_readiness(db, tenant_id=current_user.get("tenant_id"))

@router.get("/verify-ledger")
async def verify_ledger(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.VIEW_AUDITS))
):
    import hashlib
    tenant_id = current_user.get("tenant_id")
    logs = db.query(models.AuditLog).filter(models.AuditLog.tenant_id == tenant_id).order_by(models.AuditLog.timestamp.asc()).all()
    
    verified = True
    prev_hash = "0" * 64
    failures = []
    
    for idx, log in enumerate(logs):
        action_name = log.action
        user_db_id = log.user_id
        client_ip = log.ip_address
        
        raw_payload = f"{action_name}|{user_db_id}|{client_ip}|{prev_hash}"
        expected_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
        
        if log.query_hash != expected_hash:
            verified = False
            failures.append({
                "index": idx,
                "id": log.id,
                "action": log.action,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "stored_hash": log.query_hash,
                "expected_hash": expected_hash
            })
            prev_hash = log.query_hash
        else:
            prev_hash = log.query_hash
            
    return {
        "verified": verified,
        "total_logs": len(logs),
        "failures": failures,
        "hash_chain_root": prev_hash
    }
