"""
SecureCopilot 365 — FastAPI Backend
Microsoft Agents League Hackathon
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from api.routes import agents, compliance, phishing, vendor, audit, awareness, dashboard
from api.middleware.audit_log import AuditLogMiddleware
from db.database import create_tables
from auth import login as auth_login, scim as auth_scim

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SecureCopilot 365...")
    await create_tables()
    yield
    logger.info("Shutting down SecureCopilot 365...")

app = FastAPI(
    title="SecureCopilot 365 API",
    description="AI Cybersecurity, Compliance & Risk Agent for Microsoft 365",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow frontend and M365 add-ins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware: Secure Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; object-src 'none';"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Custom middleware: In-memory Rate Limiting
import time
from collections import defaultdict
RATE_LIMIT_WINDOWS = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/health_check"]:
        return await call_next(request)
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    timestamps = RATE_LIMIT_WINDOWS[client_ip]
    RATE_LIMIT_WINDOWS[client_ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW_SECONDS]
    if len(RATE_LIMIT_WINDOWS[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Rate limit exceeded (Max 100 req/min)."}
        )
    RATE_LIMIT_WINDOWS[client_ip].append(now)
    return await call_next(request)

# Custom middleware: Audit logging
app.add_middleware(AuditLogMiddleware)

# Route registration
app.include_router(auth_login.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(auth_scim.router, prefix="/api/v1/scim/v2", tags=["scim"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(phishing.router, prefix="/api/v1/phishing", tags=["phishing"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(vendor.router, prefix="/api/v1/vendor", tags=["vendor-risk"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(awareness.router, prefix="/api/v1/awareness", tags=["awareness"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SecureCopilot 365", "version": "1.0.0"}
