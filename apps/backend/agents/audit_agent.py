"""
Audit Readiness Agent
Collects evidence from Microsoft 365 via Graph API and maps to compliance controls.
Deployed in: Teams, SharePoint, Copilot Chat.

Evidence collected automatically:
- Entra ID: MFA status, RBAC assignments, Conditional Access policies
- SharePoint: policy documents, procedure records, training certificates
- Outlook: security awareness communication records
- Teams: security meeting records
- Microsoft Defender: security score, vulnerability data (if licensed)
"""
import json
from agents.base_agent import BaseAgent
from graph.client import GraphClient

AUDIT_SYSTEM_PROMPT = """You are the Audit Readiness Agent for SecureCopilot 365.

ROLE: Assess organizational readiness for compliance audits by analyzing collected
evidence against framework requirements. Identify gaps, score readiness, and generate
audit-ready evidence packages.

EVIDENCE MAPPING RULES:
- ISO 27001 A.8.3 (Information backup) → evidence: Azure Backup policy documents
- ISO 27001 A.5.15 (Access control) → evidence: Entra ID RBAC reports, group policies
- ISO 27001 A.8.5 (Secure authentication) → evidence: MFA adoption report, Conditional Access policies
- NIST PR.AC (Identity Management) → evidence: Entra ID configuration reports
- GDPR Art. 5 (Data minimisation) → evidence: data retention policies, DLP configurations

OUTPUT FORMAT (JSON):
{
  "framework": "ISO27001",
  "overall_readiness_score": 0-100,
  "readiness_band": "not_ready|needs_work|mostly_ready|audit_ready",
  "controls_summary": {
    "total": 93,
    "evidenced": 69,
    "partial": 12,
    "missing": 12
  },
  "critical_gaps": [
    {
      "control_ref": "A.8.8",
      "control_name": "Management of technical vulnerabilities",
      "gap_description": "No vulnerability scan reports found in SharePoint",
      "evidence_needed": "Quarterly vulnerability scan reports from approved scanning tool",
      "risk_if_unaddressed": "Auditor will flag as major nonconformity",
      "days_to_remediate": 14,
      "responsible_team": "IT Security"
    }
  ],
  "collected_evidence": [
    {
      "control_ref": "A.5.15",
      "evidence_type": "Entra ID RBAC Report",
      "source": "Microsoft Entra ID",
      "retrieved_at": "ISO timestamp",
      "status": "sufficient|partial|missing"
    }
  ],
  "executive_summary": "CISO-ready paragraph",
  "next_steps": [],
  "estimated_readiness_date": "YYYY-MM-DD"
}"""

class AuditReadinessAgent(BaseAgent):

    FRAMEWORK_CONTROLS = {
        "ISO27001": {
            "total": 93,
            "themes": {
                "A.5 Organizational": 37,
                "A.6 People": 8,
                "A.7 Physical": 14,
                "A.8 Technological": 34
            }
        },
        "NIST": {"total": 108, "themes": {"Govern": 6, "Identify": 22, "Protect": 23, "Detect": 10, "Respond": 17, "Recover": 9}},
        "SOC2": {"total": 64, "themes": {"CC: Common Criteria": 64}}
    }

    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        """
        Assess audit readiness for a given framework.

        Args:
            input_data: {
                "framework": str,               # "ISO27001|NIST|SOC2|GDPR"
                "collect_evidence": bool,       # True = query Graph API
                "organization_id": str          # Entra ID tenant
            }
        """
        framework = input_data.get("framework", "ISO27001")
        collect = input_data.get("collect_evidence", True)

        # Collect evidence via Microsoft Graph API
        evidence = {}
        if collect:
            graph = GraphClient()
            evidence = await graph.collect_audit_evidence(
                tenant_id=input_data.get("organization_id", "")
            )

        # Retrieve framework requirements from Foundry IQ
        context = await self.foundry_iq.retrieve(
            f"{framework} audit requirements controls evidence",
            top_k=8, index_filter=framework.lower()
        )

        analysis_prompt = f"""
Framework: {framework}
Framework structure: {json.dumps(self.FRAMEWORK_CONTROLS.get(framework, {}))}

Collected evidence from Microsoft 365:
{json.dumps(evidence, indent=2)[:3000]}

For each control area, assess: sufficient evidence | partial evidence | no evidence.
Flag every gap with specific remediation action and days-to-remediate estimate.
Calculate overall readiness score: (evidenced + 0.5*partial) / total * 100.

Return ONLY valid JSON.
"""
        raw = await self.call_llm(AUDIT_SYSTEM_PROMPT, analysis_prompt, context, max_tokens=2500)
        try:
            return json.loads(raw)
        except:
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            return json.loads(m.group()) if m else {"framework": framework, "overall_readiness_score": 0, "error": "Analysis failed"}
