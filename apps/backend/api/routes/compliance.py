"""
Compliance route
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.compliance_agent import ComplianceAdvisorAgent
from db import crud, schemas
import json

router = APIRouter()
compliance_agent = ComplianceAdvisorAgent()

@router.post("/check")
async def check_compliance(
    doc_data: dict = Body(...),
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

        analysis = await compliance_agent.analyze(doc_data, current_user)
        
        query_schema = schemas.ComplianceQueryCreate(
            employee_id=emp.id,
            document_name=doc_data.get("document_name", "Unnamed Document"),
            frameworks_checked=json.dumps(doc_data.get("frameworks", ["ISO27001", "GDPR"])),
            gaps_found=len(analysis.get("gaps", [])),
            gap_details=json.dumps(analysis.get("gaps", [])),
            remediation_provided=True,
            citations=json.dumps([gap.get("citation") for gap in analysis.get("gaps", []) if gap.get("citation")])
        )
        crud.create_compliance_query(db, query_schema)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def list_queries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.get_compliance_queries(db)
