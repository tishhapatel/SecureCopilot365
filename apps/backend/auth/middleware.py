"""
FastAPI security dependencies for JWT token decoding, active user checks, role gates, and permission scopes.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from auth import jwt_handler

# Instantiate the standard bearer token extractor
security = HTTPBearer()

async def get_current_user_from_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Extract, decode, and validate the JWT bearer token from requests."""
    token = credentials.credentials
    claims = jwt_handler.decode_token(token)
    if not claims or claims.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials"
        )
    
    user_id = claims.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Set state for audit log compatibility
    emp = db.query(models.Employee).filter(models.Employee.email == user.email).first()
    entra_id = emp.entra_id if emp else "mock-entra-id-123"
    request.state.user = {
        "id": user.id,
        "entra_id": entra_id,
        "display_name": user.display_name,
        "email": user.email,
        "department": user.department,
        "tenant_id": user.tenant_id,
        "role": user.role.role_name
    }

    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user_from_token)
) -> models.User:
    """Verify that the authenticated user profile is active in the database."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return current_user

def require_role(role_name: str):
    """Factory dependency to enforce a specific role gate on routes."""
    def dependency(user: models.User = Depends(get_current_active_user)):
        if user.role.role_name != role_name and user.role.role_name != "Super Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: role restriction"
            )
        return user
    return dependency

def require_permission(permission_name: str):
    """Factory dependency to enforce a specific permission gate on routes."""
    def dependency(user: models.User = Depends(get_current_active_user)):
        if user.role.role_name == "Super Admin":
            return user
            
        user_permissions = [p.permission_name for p in user.role.permissions]
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: permission restriction"
            )
        return user
    return dependency
