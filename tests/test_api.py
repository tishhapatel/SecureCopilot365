import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set test database url before importing backend modules
os.environ["DATABASE_URL"] = "sqlite:///./test_securecop365.db"

# Adjust path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from main import app
from db.database import engine, SessionLocal
from db.models import Base

# Client for testing FastAPI endpoints
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Make sure we clean up database from previous run if any
    Base.metadata.drop_all(bind=engine)
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    from db import models
    from datetime import datetime
    from auth.roles import ALL_ROLES
    from auth.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
    from auth.jwt_handler import hash_password
    
    # 1. Seed permissions
    permission_map = {}
    for perm in ALL_PERMISSIONS:
        db_perm = models.Permission(permission_name=perm["name"], module=perm["module"])
        db.add(db_perm)
        db.flush()
        permission_map[perm["name"]] = db_perm
        
    # 2. Seed roles
    role_map = {}
    for r_name in ALL_ROLES:
        db_role = models.Role(role_name=r_name, description=f"{r_name} system role")
        db.add(db_role)
        db.flush()
        role_map[r_name] = db_role
        
        target_perms = ROLE_PERMISSIONS.get(r_name, [])
        db_role.permissions = [permission_map[p] for p in target_perms if p in permission_map]
    db.commit()

    # Seed default employee for testing routes
    emp = models.Employee(
        entra_id="mock-entra-id-123",
        display_name="Tisha Patel",
        email="ciso@securecop.com",  # Match user email to link them
        department="Security",
        job_title="CISO",
        risk_score=35.0,
        awareness_score=82.0,
        last_training_date=datetime.utcnow()
    )
    db.add(emp)
    
    # Seed CISO User
    ciso_role = role_map["CISO"]
    user_obj = models.User(
        email="ciso@securecop.com",
        display_name="Tisha Patel",
        password_hash=hash_password("password123"),
        role_id=ciso_role.id,
        department="Security",
        tenant_id="default_tenant",
        is_active=True
    )
    db.add(user_obj)
    db.commit()
    db.close()
    yield
    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)
    # Close connection pool so we can safely delete the file
    engine.dispose()
    try:
        if os.path.exists("./test_securecop365.db"):
            os.remove("./test_securecop365.db")
    except Exception:
        pass

def get_auth_headers(email: str, password: str = "password123") -> dict:
    """Helper to authenticate a user and return request headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_agents_chat_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/agents/chat",
        json={"query": "Scan my email for phishing indicators please."},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "agent_executed" in data
    assert data["agent_executed"] == "phishing"

def test_phishing_scan_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/phishing/scan",
        json={
            "email_data": {
                "email_content": "This is a safe email body.",
                "email_subject": "Hello Friend",
                "sender_email": "friend@gmail.com"
            }
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "verdict" in data

def test_compliance_check_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/compliance/check",
        json={
            "document_text": "This draft policy doesn't define personal data protection rules.",
            "document_name": "draft_policy.txt",
            "frameworks": ["GDPR"]
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "gaps" in data

def test_vendor_assessment_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/vendor/assess",
        json={
            "vendor_name": "CloudHosting Co",
            "vendor_website": "https://cloudhosting.com"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "findings" in data

def test_audit_readiness_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    # Use /reports instead of /status
    response = client.get("/api/v1/audit/reports", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_awareness_scenario_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/awareness/scenario",
        json={"topic": "BEC"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "interactive_scenario" in data

def test_awareness_submit_endpoint():
    headers = get_auth_headers("ciso@securecop.com")
    response = client.post(
        "/api/v1/awareness/submit",
        json={"topic": "BEC", "correct": True},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["passed"] is True
