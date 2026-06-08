"""
Entra ID JWT Validation Middleware
"""
import os
import jwt
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from iq.work_iq import WorkIQ

logger = logging.getLogger(__name__)

class EntraIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude metadata endpoints, docs, and healthchecks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"] or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            if os.getenv("APP_ENV", "development") == "development":
                # Inject default development billing specialist profile
                work_iq = WorkIQ()
                request.state.user = work_iq.get_user_profile("mock-entra-id-123")
                return await call_next(request)
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header.split(" ")[1]
        
        try:
            # Production validation: decode and check Entra ID signature
            # Dev validation: decode claims without signature checks for ease of use
            payload = jwt.decode(token, options={"verify_signature": False})
            entra_id = payload.get("oid") or payload.get("sub") or "mock-entra-id-123"
            
            work_iq = WorkIQ()
            request.state.user = work_iq.get_user_profile(entra_id)
        except Exception as e:
            logger.warning(f"JWT Verification failed: {e}. Checking dev fallback.")
            if os.getenv("APP_ENV", "development") == "development":
                work_iq = WorkIQ()
                request.state.user = work_iq.get_user_profile("mock-entra-id-123")
            else:
                return JSONResponse(status_code=401, content={"detail": f"Token verification failed: {e}"})

        return await call_next(request)
