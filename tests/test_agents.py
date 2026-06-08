import os
import sys
import pytest

# Adjust path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from agents.orchestrator import OrchestratorAgent
from agents.phishing_agent import PhishingDetectionAgent
from agents.compliance_agent import ComplianceAdvisorAgent
from agents.vendor_agent import VendorRiskAgent
from agents.audit_agent import AuditReadinessAgent
from agents.awareness_agent import SecurityAwarenessCoach

mock_user = {
    "entra_id": "mock-entra-id-123",
    "display_name": "Tisha Patel",
    "email": "tisha.patel@enterprise.com",
    "department": "Finance",
    "job_title": "Billing Specialist",
    "risk_score": 35.0,
    "awareness_score": 82.0
}

@pytest.mark.asyncio
async def test_orchestrator_routing():
    agent = OrchestratorAgent()
    query = "Scan my email for phishing indicators please."
    result = await agent.route_and_analyze(query, mock_user)
    
    assert result is not None
    assert "agent_executed" in result
    assert result["agent_executed"] == "phishing"
    assert "analysis" in result

@pytest.mark.asyncio
async def test_phishing_agent_low_risk():
    agent = PhishingDetectionAgent()
    email_data = {
        "email_content": "Hello Team, please find our weekly news update attached.",
        "email_subject": "Weekly Newsletter",
        "sender_email": "newsletter@safebrand.com",
        "sender_display": "Weekly News",
        "spf_result": "pass",
        "dkim_result": "pass",
        "dmarc_result": "pass"
    }
    result = await agent.analyze(email_data, mock_user)
    
    assert result is not None
    assert "risk_score" in result
    assert result["risk_score"] < 30
    assert result["verdict"] == "safe"

@pytest.mark.asyncio
async def test_phishing_agent_high_risk():
    agent = PhishingDetectionAgent()
    email_data = {
        "email_content": "URGENT: Your account password has expired. Click here immediately to verify: http://lookalike-microsoft.com/reset.",
        "email_subject": "Security Alert: Verify your account immediately",
        "sender_email": "support@lookalike-microsoft.com",
        "sender_display": "Microsoft Security Team",
        "spf_result": "fail",
        "dkim_result": "none",
        "dmarc_result": "fail"
    }
    result = await agent.analyze(email_data, mock_user)
    
    assert result is not None
    assert "risk_score" in result
    assert result["risk_score"] > 60
    assert result["verdict"] in ["phishing", "bec_attempt"]
    assert len(result["indicators"]) > 0

@pytest.mark.asyncio
async def test_compliance_agent():
    agent = ComplianceAdvisorAgent()
    doc_data = {
        "document_text": "This draft vendor contract governs customer data processing. It does not contain breach notification requirements.",
        "document_name": "draft_sla.docx",
        "frameworks": ["ISO27001", "GDPR"],
        "document_type": "contract"
    }
    result = await agent.analyze(doc_data, mock_user)
    
    assert result is not None
    assert "compliance_score" in result
    assert len(result["gaps"]) > 0
    assert result["pii_detected"] is True

@pytest.mark.asyncio
async def test_vendor_risk_agent():
    agent = VendorRiskAgent()
    vendor_data = {
        "vendor_name": "Proposed Vendor Corp",
        "vendor_website": "http://proposed-vendor-corp.com",
        "data_categories": ["personal_data_pii"]
    }
    result = await agent.analyze(vendor_data, mock_user)
    
    assert result is not None
    assert "risk_score" in result
    assert "risk_tier" in result
    assert len(result["findings"]) > 0

@pytest.mark.asyncio
async def test_audit_readiness_agent():
    agent = AuditReadinessAgent()
    audit_data = {
        "framework": "ISO27001",
        "collect_evidence": True
    }
    result = await agent.analyze(audit_data, mock_user)
    
    assert result is not None
    assert "overall_readiness_score" in result
    assert "controls_summary" in result
    assert len(result["critical_gaps"]) > 0

@pytest.mark.asyncio
async def test_awareness_coach():
    agent = SecurityAwarenessCoach()
    coach_data = {
        "topic": "BEC"
    }
    result = await agent.analyze(coach_data, mock_user)
    
    assert result is not None
    assert "interactive_scenario" in result
    assert "quiz" in result["interactive_scenario"] or "question" in result["interactive_scenario"]
