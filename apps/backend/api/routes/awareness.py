"""
Security Awareness Coach routes
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_user
from agents.awareness_agent import SecurityAwarenessCoach
from db import crud, schemas
from datetime import datetime

router = APIRouter()
coach = SecurityAwarenessCoach()

@router.post("/scenario")
async def get_scenario(
    payload: dict = Body(...),
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
            
        user_context = {
            "department": emp.department,
            "job_title": emp.job_title,
            "risk_score": emp.risk_score,
            "awareness_score": emp.awareness_score
        }
        
        analysis = await coach.analyze(payload, user_context)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_response(
    submission: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        emp = crud.get_employee_by_entra_id(db, current_user.get("entra_id"))
        if not emp:
            raise HTTPException(status_code=404, detail="Employee profile not found")

        completion_schema = schemas.TrainingCompletionCreate(
            employee_id=emp.id,
            topic=submission.get("topic", "General Phishing"),
            score=100.0 if submission.get("correct") else 0.0,
            passed=submission.get("correct")
        )
        crud.create_training_completion(db, completion_schema)

        # Correct answer improves awareness, incorrect raises risk indices
        score_change = 4.0 if submission.get("correct") else -2.0
        new_awareness = round(max(0.0, min(100.0, emp.awareness_score + score_change)), 1)
        
        risk_reduction = 1.5 if submission.get("correct") else -3.0
        new_risk = round(max(0.0, min(100.0, emp.risk_score - risk_reduction)), 1)
        
        crud.update_employee_scores(db, emp.id, new_risk, new_awareness)
        
        emp.last_training_date = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "passed": submission.get("correct"),
            "new_awareness_score": new_awareness,
            "new_risk_score": new_risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
