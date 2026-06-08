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
from api.middleware.auth import EntraIDMiddleware
from api.middleware.audit_log import AuditLogMiddleware
from db.database import create_tables

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

# Custom middleware: Entra ID JWT validation and audit logging
app.add_middleware(AuditLogMiddleware)
app.add_middleware(EntraIDMiddleware)

# Route registration
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
