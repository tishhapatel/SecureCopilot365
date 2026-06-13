"""
SCIM 2.0 (System for Cross-domain Identity Management) Provisioning Endpoints.
Allows Entra ID to push active user sync events automatically to SecureCopilot 365.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from db.database import get_db
from db import models, crud, schemas
from auth.middleware import get_current_active_user, require_permission
from auth import permissions
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# SCIM Schema Representation
class SCIMName(BaseModel):
    formatted: str
    familyName: Optional[str] = None
    givenName: Optional[str] = None

class SCIMEmail(BaseModel):
    value: str
    primary: bool = True
    type: str = "work"

class SCIMUserCreate(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    userName: str # This maps to email
    name: SCIMName
    emails: List[SCIMEmail]
    active: bool = True
    department: Optional[str] = "General"

@router.get("/Users")
async def list_scim_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Retrieve all users in SCIM list format for the tenant."""
    users = crud.get_users_by_tenant(db, tenant_id=current_user.tenant_id)
    resources = []
    for u in users:
        resources.append({
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": u.id,
            "userName": u.email,
            "displayName": u.display_name,
            "emails": [{"value": u.email, "primary": True}],
            "active": u.is_active,
            "meta": {"resourceType": "User", "created": u.created_at.isoformat()}
        })
        
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "itemsPerPage": 100,
        "startIndex": 1,
        "Resources": resources
    }

@router.post("/Users", status_code=201)
async def create_scim_user(
    payload: SCIMUserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """SCIM creation endpoint to provision new directory profiles from Entra ID."""
    # Check if user already exists
    existing = crud.get_user_by_email(db, payload.userName)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists in directory")

    import secrets
    # Sync using standard CRUD schema
    user_schema = schemas.UserCreate(
        email=payload.userName,
        display_name=payload.name.formatted,
        password=f"Temp_{secrets.token_urlsafe(12)}!", # Secure randomly generated initial password
        role_name="General Employee",
        department=payload.department
    )
    
    db_user = crud.create_user(db, user_schema, tenant_id=current_user.tenant_id)
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": db_user.id,
        "userName": db_user.email,
        "displayName": db_user.display_name,
        "emails": [{"value": db_user.email, "primary": True}],
        "active": db_user.is_active,
        "meta": {"resourceType": "User", "created": db_user.created_at.isoformat()}
    }

@router.patch("/Users/{id}")
async def patch_scim_user(
    id: str,
    operations: dict, # Standard SCIM patch payload containing operations (Replace active / role states)
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """SCIM patch endpoint to toggle states or change values."""
    db_user = db.query(models.User).filter(models.User.id == id, models.User.tenant_id == current_user.tenant_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    ops = operations.get("Operations", [])
    for op in ops:
        if op.get("op").lower() == "replace":
            value = op.get("value", {})
            if "active" in value:
                crud.update_user_activation(db, user_id=id, is_active=value["active"], tenant_id=current_user.tenant_id)

    return Response(status_code=204)

@router.delete("/Users/{id}", status_code=204)
async def delete_scim_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Deprovision user profile immediately from directory."""
    success = crud.delete_user(db, user_id=id, tenant_id=current_user.tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)
