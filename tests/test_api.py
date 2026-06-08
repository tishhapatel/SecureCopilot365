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
    
    # Seed default employee for testing routes
    db = SessionLocal()
    from db import models
    from datetime import datetime
    emp = models.Employee(
        entra_id="mock-entra-id-123",
        display_name="Tisha Patel",
        email="tisha.patel@enterprise.com",
        department="Finance",
        job_title="Billing Specialist",
        risk_score=35.0,
        awareness_score=82.0,
        last_training_date=datetime.utcnow()
    )
    db.add(emp)
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

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_agents_chat_endpoint():
    response = client.post(
        "/api/v1/agents/chat",
        json={"query": "Scan my email for phishing indicators please."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "agent_executed" in data
    assert data["agent_executed"] == "phishing"

def test_phishing_scan_endpoint():
    response = client.post(
        "/api/v1/phishing/scan",
        json={
            "email_content": "This is a safe email body.",
            "email_subject": "Hello Friend",
            "sender_email": "friend@gmail.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "verdict" in data

def test_compliance_check_endpoint():
    response = client.post(
        "/api/v1/compliance/check",
        json={
            "document_text": "This draft policy doesn't define personal data protection rules.",
            "document_name": "draft_policy.txt",
            "frameworks": ["GDPR"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "gaps" in data

def test_vendor_assessment_endpoint():
    response = client.post(
        "/api/v1/vendor/assess",
        json={
            "vendor_name": "CloudHosting Co",
            "vendor_website": "https://cloudhosting.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "findings" in data

def test_audit_readiness_endpoint():
    # Use /reports instead of /status
    response = client.get("/api/v1/audit/reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_awareness_scenario_endpoint():
    response = client.post(
        "/api/v1/awareness/scenario",
        json={"topic": "BEC"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "interactive_scenario" in data

def test_awareness_submit_endpoint():
    response = client.post(
        "/api/v1/awareness/submit",
        json={"topic": "BEC", "correct": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["passed"] is True
