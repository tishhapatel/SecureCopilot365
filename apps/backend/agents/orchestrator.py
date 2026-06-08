"""
Orchestrator Agent
Routes incoming queries to the appropriate security sub-agent.
"""
import json
import logging
from agents.base_agent import BaseAgent
from agents.phishing_agent import PhishingDetectionAgent
from agents.compliance_agent import ComplianceAdvisorAgent
from agents.vendor_agent import VendorRiskAgent
from agents.audit_agent import AuditReadinessAgent
from agents.awareness_agent import SecurityAwarenessCoach

logger = logging.getLogger(__name__)

ORCHESTRATOR_SYSTEM_PROMPT = """You are the Master Orchestrator Agent for SecureCopilot 365.

Your role: Classify user queries and route them to the correct security sub-agent.

Available Sub-Agents:
1. `phishing` (Phishing Detection): Analyze email content, headers, BEC requests, urgency patterns.
2. `compliance` (Compliance Advisor): Analyze documents, contracts, policies for compliance gaps against GDPR, ISO 27001, NIST.
3. `vendor` (Vendor Risk Scorer): Assess vendor security profiles, questionnaires, certs.
4. `audit` (Audit Readiness): Review evidence from Graph API for audit readiness reports.
5. `awareness` (Security Awareness Coach): Provide interactive security quizzes and role-specific training scenarios.

OUTPUT FORMAT (JSON):
{
  "selected_agent": "phishing|compliance|vendor|audit|awareness",
  "confidence": 0.0-1.0,
  "routing_rationale": "one sentence explaining why this agent was chosen",
  "redirect_suggested": "optional suggestions or corrections if user is slightly off topic"
}"""

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agents = {
            "phishing": PhishingDetectionAgent(),
            "compliance": ComplianceAdvisorAgent(),
            "vendor": VendorRiskAgent(),
            "audit": AuditReadinessAgent(),
            "awareness": SecurityAwarenessCoach()
        }

    async def route_and_analyze(self, query: str, user_context: dict, file_data: dict = None) -> dict:
        """
        Classifies the query, invokes the target agent, and returns the unified payload.
        """
        if file_data is None:
            file_data = {}
        # Sanitization
        sanitized_query = self.sanitize_input(query)

        # Prompt LLM for classification
        raw_classification = await self.call_llm(
            ORCHESTRATOR_SYSTEM_PROMPT,
            f"Classify this user request: '{sanitized_query}'"
        )

        try:
            route_info = json.loads(raw_classification)
        except Exception:
            # Fallback regex classification
            route_info = self._regex_classify(sanitized_query)

        agent_name = route_info.get("selected_agent", "awareness")
        if agent_name not in self.agents:
            agent_name = "awareness"

        # Prepare payload for target agent
        target_agent = self.agents[agent_name]
        
        # Build analysis request payload based on the route
        input_payload = {}
        if agent_name == "phishing":
            input_payload = {
                "email_content": file_data.get("content") if file_data else sanitized_query,
                "email_subject": file_data.get("subject", "Copilot Phishing Query"),
                "sender_email": file_data.get("sender", "unknown@domain.com"),
                "sender_display": file_data.get("sender_display", "External Sender"),
                "spf_result": file_data.get("spf_result", "none") if file_data else "none",
                "dkim_result": file_data.get("dkim_result", "none") if file_data else "none",
                "dmarc_result": file_data.get("dmarc_result", "none") if file_data else "none",
                "links": file_data.get("links", []) if file_data else [],
                "attachments": file_data.get("attachments", []) if file_data else []
            }
        elif agent_name == "compliance":
            input_payload = {
                "document_text": file_data.get("content") if file_data else sanitized_query,
                "document_name": file_data.get("name", "Copilot Input"),
                "frameworks": ["ISO27001", "GDPR", "NIST"],
                "document_type": file_data.get("document_type", "general") if file_data else "general"
            }
        elif agent_name == "vendor":
            # Extract basic vendor info from query or data
            input_payload = {
                "vendor_name": file_data.get("vendor_name") or "Proposed Vendor",
                "vendor_website": file_data.get("vendor_website") or "http://proposed-vendor.com",
                "data_categories": file_data.get("data_categories") or ["personal_data_pii"],
                "certifications": file_data.get("certifications") or {"iso27001": True},
                "questionnaire_responses": file_data.get("questionnaire_responses") or {"mfa_enabled": True},
                "pen_test_date": file_data.get("pen_test_date") or "2025-12-01",
                "sub_processors": file_data.get("sub_processors") or [],
                "incident_history": file_data.get("incident_history") or [],
                "dpa_signed": file_data.get("dpa_signed", True)
            }
        elif agent_name == "audit":
            input_payload = {
                "framework": "ISO27001",
                "collect_evidence": True,
                "organization_id": user_context.get("tenant_id", "default_tenant")
            }
        elif agent_name == "awareness":
            input_payload = {
                "topic": file_data.get("topic") if file_data else None,
                "level": "intermediate"
            }

        # Execute target analysis
        analysis_result = await target_agent.analyze(input_payload, user_context)

        return {
            "routing": route_info,
            "agent_executed": agent_name,
            "analysis": analysis_result
        }

    def _regex_classify(self, query: str) -> dict:
        q = query.lower()
        if any(x in q for x in ["phish", "spam", "email", "link", "scam"]):
            return {"selected_agent": "phishing", "confidence": 0.8, "routing_rationale": "Regex match on email terms"}
        if any(x in q for x in ["gdpr", "iso", "compliance", "policy", "clause", "regulation"]):
            return {"selected_agent": "compliance", "confidence": 0.8, "routing_rationale": "Regex match on compliance terms"}
        if any(x in q for x in ["vendor", "third party", "supplier", "tprm"]):
            return {"selected_agent": "vendor", "confidence": 0.8, "routing_rationale": "Regex match on vendor terms"}
        if any(x in q for x in ["audit", "evidence", "readiness", "readiness report"]):
            return {"selected_agent": "audit", "confidence": 0.8, "routing_rationale": "Regex match on audit terms"}
        return {"selected_agent": "awareness", "confidence": 0.6, "routing_rationale": "Defaulting to Security Awareness"}

    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        # Implements BaseAgent requirements
        return await self.route_and_analyze(input_data.get("query", ""), user_context)
