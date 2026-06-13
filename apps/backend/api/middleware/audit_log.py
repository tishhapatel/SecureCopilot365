"""
Immutable Audit Logging Middleware
"""
import hashlib
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from db.database import SessionLocal
from db.models import AuditLog

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Let the request execute
        response = await call_next(request)
        
        # Exclude documentation or health paths
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"] or request.method == "OPTIONS":
            return response

        # Fetch authenticated user profile if available
        user = getattr(request.state, "user", None)
        user_entra_id = user.get("entra_id") if user else "anonymous"
        user_db_id = user.get("id") if user else None
        tenant_id = user.get("tenant_id", "default_tenant") if user else "default_tenant"
        client_ip = request.client.host if request.client else "127.0.0.1"
        action_name = f"{request.method} {request.url.path}"

        db = SessionLocal()
        try:
            # Retrieve previous audit log entry for the tenant to build the chain
            last_log = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id).order_by(AuditLog.timestamp.desc()).first()
            prev_hash = last_log.query_hash if last_log and last_log.query_hash else "0" * 64
            
            # Compute current block hash: SHA-256(Action || UserID || ClientIP || PrevHash)
            raw_payload = f"{action_name}|{user_db_id}|{client_ip}|{prev_hash}"
            current_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

            # Classify risk level based on access path
            risk_level = "low"
            if "admin" in request.url.path.lower() or request.method in ["POST", "PUT", "DELETE"]:
                risk_level = "medium"
            if "delete" in request.url.path.lower() or "deactivate" in request.url.path.lower():
                risk_level = "high"

            log_entry = AuditLog(
                user_entra_id=user_entra_id,
                user_id=user_db_id,
                action=action_name,
                agent=request.url.path.split("/")[-1] or "gateway",
                query_hash=current_hash,
                response_category="SaaS Audit Chain",
                risk_level=risk_level,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", "Unknown"),
                tenant_id=tenant_id
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            # Silence logging write failures to avoid breaking primary requests
            pass
        finally:
            db.close()

        return response

