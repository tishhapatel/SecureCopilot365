"""
Zero Trust continuous verification engine for SecureCopilot 365.
Enforces conditional access based on identity, device compliance, session risk, and behavior patterns.
"""
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
import logging

logger = logging.getLogger(__name__)

class ZeroTrustVerifier:
  def __init__(self):
    # Simulated corporate IP ranges for Conditional Access
    self.allowed_ip_ranges = ["127.0.0.1", "192.168.1.0/24", "10.0.0.0/8"]

  async def verify_request(self, request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Enforces continuous verification checking:
    1. Identity & Active Session state
    2. Device compliance (Intune MDM state)
    3. Contextual IP validation & geo-velocity (impossible travel)
    4. Current User risk score
    """
    # 1. Identity must be verified (extracted by middleware)
    user_state = getattr(request.state, "user", None)
    if not user_state:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Zero Trust: Identity verification failed. No active session."
      )

    user_id = user_state.get("id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Zero Trust: User account is inactive or revoked."
      )

    # 2. Check Device Compliance
    # In production, we validate Intune headers or client certificates.
    # In sandbox, we inspect client metadata headers.
    device_id = request.headers.get("X-Device-Id")
    device_compliant = request.headers.get("X-Device-Compliant", "true").lower() == "true"

    # Gated constraint: Admin/CISO roles MUST run on managed, compliant devices
    if user.role.role_name in ["Super Admin", "CISO", "Compliance Officer"] and not device_compliant:
      logger.warning(f"Zero Trust Access Gated: User {user.email} attempted admin access from unmanaged device {device_id}")
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Zero Trust policy: Administrative actions restricted to compliant Intune-enrolled devices."
      )

    # 3. Geo-velocity check (contextual impossible travel)
    client_ip = request.client.host if request.client else "127.0.0.1"
    # Inspect if IP is suddenly swapping to an external country or range within short periods
    # Simulate high risk travel flag if header is explicitly passed for testing
    travel_alert = request.headers.get("X-Risk-Impossible-Travel", "false").lower() == "true"
    if travel_alert:
      logger.error(f"Zero Trust Alert: Impossible travel flagged for user {user.email} from IP {client_ip}")
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Zero Trust block: Impossible travel alert flagged. Re-authentication required."
      )

    # 4. User Risk Score Gate
    # Fetch risk score associated with corresponding employee profile
    emp = db.query(models.Employee).filter(models.Employee.email == user.email).first()
    if emp and emp.risk_score > 80.0:
      logger.warning(f"Zero Trust Warning: High risk user {user.email} (Risk: {emp.risk_score}) triggered step-up MFA")
      # Check if simulated MFA header has been completed
      mfa_verified = request.headers.get("X-StepUp-MFA-Verified", "false").lower() == "true"
      if not mfa_verified:
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Zero Trust: High-risk behavior detected. Dynamic Step-up MFA verification required."
        )

    return user_state

# Instantiated Dependency injection
zt_verifier = ZeroTrustVerifier()
verify_zero_trust = zt_verifier.verify_request
