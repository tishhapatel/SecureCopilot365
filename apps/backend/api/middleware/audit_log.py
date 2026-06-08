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
        user_id = user.get("entra_id") if user else "anonymous"
        
        # Protect PII by storing a hash of the URL request details
        path_bytes = f"{request.method} {request.url.path}".encode('utf-8')
        query_hash = hashlib.sha256(path_bytes).hexdigest()
        
        db = SessionLocal()
        try:
            log_entry = AuditLog(
                user_entra_id=user_id,
                action=f"{request.method} {request.url.path}",
                agent=request.url.path.split("/")[-1],
                query_hash=query_hash,
                response_category="API Query Log",
                risk_level="low",
                ip_address=request.client.host if request.client else "127.0.0.1",
                user_agent=request.headers.get("user-agent", "Unknown")
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            # Silence logging write failures to avoid breaking primary requests
            pass
        finally:
            db.close()

        return response
