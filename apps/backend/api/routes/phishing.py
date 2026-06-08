"""
Phishing route
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.phishing_agent import PhishingDetectionAgent
from db import crud, schemas
import json

router = APIRouter()
phishing_agent = PhishingDetectionAgent()

@router.post("/scan")
async def scan_email(
    email_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        emp = crud.get_employee_by_entra_id(db, current_user.get("entra_id"))
        if not emp:
            emp_schema = schemas.EmployeeCreate(
                entra_id=current_user.get("entra_id"),
                display_name=current_user.get("display_name"),
                email=current_user.get("email"),
                department=current_user.get("department"),
                job_title=current_user.get("job_title")
            )
            emp = crud.create_employee(db, emp_schema)

        analysis = await phishing_agent.analyze(email_data, current_user)
        
        incident_schema = schemas.PhishingIncidentCreate(
            employee_id=emp.id,
            email_subject=email_data.get("email_subject", "No Subject"),
            sender_domain=email_data.get("sender_email", "unknown@domain.com").split("@")[-1],
            risk_score=float(analysis.get("risk_score", 0)),
            risk_level=analysis.get("risk_level", "low"),
            mitre_techniques=json.dumps(analysis.get("mitre_techniques", [])),
            indicators=json.dumps(analysis.get("indicators", [])),
            user_action="analyzed",
            reported_to_soc=analysis.get("report_to_soc", False)
        )
        crud.create_phishing_incident(db, incident_schema)
        
        # Adjust risk score based on finding
        new_risk = round(max(emp.risk_score, float(analysis.get("risk_score", 0)) * 0.25), 1)
        crud.update_employee_scores(db, emp.id, new_risk, emp.awareness_score)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents")
async def list_incidents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.get_phishing_incidents(db)
