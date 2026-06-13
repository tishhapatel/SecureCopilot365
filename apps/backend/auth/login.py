"""
FastAPI endpoints for authentication, SSO callback, token refresh, and user profile operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import models, schemas
from auth import jwt_handler, roles, oauth
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
entra_auth = oauth.EntraIDAuth()

class EntraCallbackRequest(BaseModel):
    code: str
    tenant_id: Optional[str] = "tenant-alpha"
    role_name: Optional[str] = "General Employee"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=schemas.TokenResponse)
async def login_local(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate username and password locally (development portal login)."""
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not jwt_handler.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Generate authentication payload
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.role_name,
        "tenant_id": user.tenant_id
    }
    access_token = jwt_handler.create_access_token(token_data)
    refresh_token = jwt_handler.create_refresh_token(token_data)
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }

@router.get("/entra/url")
async def get_entra_login_url():
    """Retrieve the redirect URL for Microsoft Azure Entra ID Sign-In."""
    return {"url": entra_auth.get_authorization_url()}

@router.post("/entra/callback", response_model=schemas.TokenResponse)
async def login_entra_callback(payload: EntraCallbackRequest, db: Session = Depends(get_db)):
    """Validate Microsoft Entra OAuth 2.0 codes and match profiles in the DB."""
    profile = await entra_auth.exchange_code_for_user(payload.code)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entra ID code validation failed"
        )
        
    # Get user by email
    email = profile["email"]
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Match appropriate role
    target_role_name = payload.role_name or profile.get("job_title") or roles.EMPLOYEE
    db_role = db.query(models.Role).filter(models.Role.role_name == target_role_name).first()
    if not db_role:
        # Standard fallback if job title does not map to direct role
        db_role = db.query(models.Role).filter(models.Role.role_name == roles.EMPLOYEE).first()
        
    target_tenant_id = payload.tenant_id or profile.get("tenant_id") or "tenant-alpha"
    
    if not user:
        # Register user on the fly for SSO logins
        user = models.User(
            email=email,
            display_name=profile["display_name"],
            role_id=db_role.id,
            department=profile["department"] or "General",
            tenant_id=target_tenant_id,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Sync profile information
        user.display_name = profile["display_name"]
        user.department = profile["department"] or user.department
        user.tenant_id = target_tenant_id
        user.role_id = db_role.id
        db.commit()
        db.refresh(user)
        
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": db_role.role_name,
        "tenant_id": user.tenant_id
    }
    access_token = jwt_handler.create_access_token(token_data)
    refresh_token = jwt_handler.create_refresh_token(token_data)
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }

@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_tokens(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Issue a new access token using an active refresh token."""
    claims = jwt_handler.decode_token(payload.refresh_token)
    if not claims or claims.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    user_id = claims.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )
        
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.role_name,
        "tenant_id": user.tenant_id
    }
    access_token = jwt_handler.create_access_token(token_data)
    refresh_token = jwt_handler.create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }

# Delay imports for circular dependencies
from auth.middleware import get_current_active_user, require_permission
from auth import permissions
from db import crud
from typing import List

class UpdateUserRoleRequest(BaseModel):
    role_name: str

class UpdateUserActivationRequest(BaseModel):
    is_active: bool

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_profile(current_user: models.User = Depends(get_current_active_user)):
    """Retrieve logged-in user profile attributes."""
    return current_user

@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """List all users in the current tenant."""
    return crud.get_users_by_tenant(db, tenant_id=current_user.tenant_id)

@router.post("/users", response_model=schemas.UserResponse)
async def register_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Create a new user within the current tenant."""
    try:
        user = crud.create_user(db, payload, tenant_id=current_user.tenant_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/users/{user_id}/role", response_model=schemas.UserResponse)
async def change_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Update a user's role within the current tenant."""
    updated_user = crud.update_user_role(db, user_id=user_id, role_name=payload.role_name, tenant_id=current_user.tenant_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User or Role not found in this tenant")
    return updated_user

@router.put("/users/{user_id}/activation", response_model=schemas.UserResponse)
async def toggle_user_activation(
    user_id: str,
    payload: UpdateUserActivationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Toggle activation state for a user within the current tenant."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    updated_user = crud.update_user_activation(db, user_id=user_id, is_active=payload.is_active, tenant_id=current_user.tenant_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found in this tenant")
    return updated_user

@router.delete("/users/{user_id}")
async def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Delete a user account from the tenant."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    success = crud.delete_user(db, user_id=user_id, tenant_id=current_user.tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found in this tenant")
    return {"message": "User deleted successfully"}

@router.get("/roles", response_model=List[schemas.RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all available system roles."""
    return db.query(models.Role).all()

import hashlib

@router.get("/audit_logs/verify")
async def verify_audit_ledger(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.VIEW_AUDITS))
):
    """
    Forensically validates the integrity of the audit log ledger chain for the tenant.
    Computes H_n = SHA256(Action || UserID || ClientIP || H_{n-1}) and compares it.
    """
    logs = db.query(models.AuditLog).filter(models.AuditLog.tenant_id == current_user.tenant_id).order_by(models.AuditLog.timestamp.asc()).all()
    
    if not logs:
        return {"status": "empty", "message": "No audit logs found for verification."}
        
    expected_prev_hash = "0" * 64
    errors = []
    
    for i, log in enumerate(logs):
        raw_payload = f"{log.action}|{log.user_id}|{log.ip_address}|{expected_prev_hash}"
        computed_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
        
        if log.query_hash != computed_hash:
            errors.append({
                "index": i,
                "log_id": log.id,
                "recorded_hash": log.query_hash,
                "computed_hash": computed_hash,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            })
        expected_prev_hash = log.query_hash
        
    if errors:
        return {
            "status": "tampered",
            "message": f"Ledger verification failed! Detected {len(errors)} tampered block(s).",
            "errors": errors
        }
        
    return {
        "status": "verified",
        "message": f"Audit ledger chain successfully validated. All {len(logs)} records are intact and cryptographically chained."
    }

@router.get("/audit_logs", response_model=List[schemas.AuditLog])
async def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission(permissions.VIEW_AUDITS))
):
    """Retrieve all audit logs for the current tenant."""
    return crud.get_audit_logs(db, tenant_id=current_user.tenant_id)


# Simulated tenant data residency storage
TENANT_DATA_RESIDENCY = {}

class DataResidencyUpdate(BaseModel):
    region: str

@router.get("/data-residency")
async def get_data_residency(
    current_user: models.User = Depends(get_current_active_user)
):
    """Retrieve data residency configuration for the tenant."""
    tenant_id = current_user.tenant_id
    region = TENANT_DATA_RESIDENCY.get(tenant_id, "East US (Primary)")
    return {"tenant_id": tenant_id, "region": region}

@router.post("/data-residency")
async def update_data_residency(
    payload: DataResidencyUpdate,
    current_user: models.User = Depends(require_permission(permissions.MANAGE_USERS))
):
    """Update data residency configuration for the tenant."""
    tenant_id = current_user.tenant_id
    TENANT_DATA_RESIDENCY[tenant_id] = payload.region
    return {"status": "success", "tenant_id": tenant_id, "region": payload.region}

