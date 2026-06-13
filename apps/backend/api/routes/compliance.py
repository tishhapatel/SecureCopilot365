"""
Compliance route
"""
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_with_permission
from agents.compliance_agent import ComplianceAdvisorAgent
from db import crud, schemas
from auth import permissions
from utils.upload_scanner import validate_file_upload
import json

router = APIRouter()
compliance_agent = ComplianceAdvisorAgent()

@router.post("/upload")
async def upload_compliance_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.RUN_COMPLIANCE))
):
    try:
        content = await file.read()
        # Enforce security scanning (blocks EICAR, macros, javascript, unsafe extensions)
        validate_file_upload(file.filename, content)
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' passed all security scanning checks.",
            "file_name": file.filename,
            "file_size": len(content)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def check_compliance(
    doc_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.RUN_COMPLIANCE))
):
    try:
        emp = crud.get_employee_by_entra_id(db, current_user.get("entra_id"), tenant_id=current_user.get("tenant_id"))
        if not emp:
            emp_schema = schemas.EmployeeCreate(
                entra_id=current_user.get("entra_id"),
                display_name=current_user.get("display_name"),
                email=current_user.get("email"),
                department=current_user.get("department"),
                job_title=current_user.get("job_title")
            )
            emp = crud.create_employee(db, emp_schema, tenant_id=current_user.get("tenant_id"))

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
        crud.create_compliance_query(db, query_schema, tenant_id=current_user.get("tenant_id"))
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def list_queries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_with_permission(permissions.VIEW_COMPLIANCE))
):
    return crud.get_compliance_queries(db, tenant_id=current_user.get("tenant_id"))
