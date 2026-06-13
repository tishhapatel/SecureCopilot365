from fastapi import Depends, Request
from sqlalchemy.orm import Session
from db.database import get_db
from auth.middleware import get_current_active_user, require_permission
from auth.zero_trust import verify_zero_trust
from db import models

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_active_user),
    zt_user: dict = Depends(verify_zero_trust)
) -> dict:
    """
    Returns the authenticated user details by decoding the JWT access token.
    Enforces continuous zero-trust validation checks.
    Provides backwards compatibility for endpoints expecting an Active Directory profile.
    """
    emp = db.query(models.Employee).filter(models.Employee.email == user.email).first()
    entra_id = emp.entra_id if emp else "mock-entra-id-123"
    
    return {
        "id": user.id,
        "entra_id": entra_id,
        "display_name": user.display_name,
        "email": user.email,
        "department": user.department,
        "job_title": user.role.role_name,
        "tenant_id": user.tenant_id,
        "role": user.role.role_name
    }

def get_user_with_permission(permission_name: str):
    """
    Returns a dependency that validates the user has the specified permission,
    enforces zero-trust verifications, and returns the compatibility profile dictionary.
    """
    async def dependency(
        request: Request,
        db: Session = Depends(get_db),
        user: models.User = Depends(require_permission(permission_name)),
        zt_user: dict = Depends(verify_zero_trust)
    ) -> dict:
        emp = db.query(models.Employee).filter(models.Employee.email == user.email).first()
        entra_id = emp.entra_id if emp else "mock-entra-id-123"
        return {
            "id": user.id,
            "entra_id": entra_id,
            "display_name": user.display_name,
            "email": user.email,
            "department": user.department,
            "job_title": user.role.role_name,
            "tenant_id": user.tenant_id,
            "role": user.role.role_name
        }
    return dependency

