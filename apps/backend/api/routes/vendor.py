"""
Vendor Risk route
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.vendor_agent import VendorRiskAgent
from db import crud, schemas
import json

router = APIRouter()
vendor_agent = VendorRiskAgent()

@router.post("/assess")
async def assess_vendor(
    vendor_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        analysis = await vendor_agent.analyze(vendor_data, current_user)
        
        vendor_schema = schemas.VendorCreate(
            name=vendor_data.get("vendor_name", "Unnamed Vendor"),
            website=vendor_data.get("vendor_website"),
            data_categories=json.dumps(vendor_data.get("data_categories", [])),
            iso27001_certified=vendor_data.get("certifications", {}).get("iso27001", False),
            soc2_type2=vendor_data.get("certifications", {}).get("soc2_type2", False),
            gdpr_dpa_signed=vendor_data.get("dpa_signed", False),
            sub_processors=json.dumps(vendor_data.get("sub_processors", [])),
            questionnaire_score=float(analysis.get("dimension_scores", {}).get("questionnaire", {}).get("score", 50.0)),
            pen_test_date=None,
            incident_history=json.dumps(vendor_data.get("incident_history", [])),
            notes=analysis.get("risk_summary")
        )
        db_vendor = crud.create_vendor(db, vendor_schema)
        # Apply the final agent risk score directly
        db_vendor.risk_score = float(analysis.get("risk_score", 50.0))
        db.commit()
        db.refresh(db_vendor)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_vendors(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.get_vendors(db)
