"""
Compliance Advisor Agent
Analyzes documents and policies against multiple compliance frameworks.
Frameworks: ISO 27001:2022, NIST CSF 2.0, GDPR, HIPAA, SOC 2, CIS Controls v8.
Deployed in: Word sidebar, SharePoint, Teams.

Capabilities:
- Gap analysis against selected frameworks
- Control mapping to specific articles/clauses
- Remediation language generation
- Data handling risk identification
- PII exposure detection
- GDPR lawful basis verification
"""
import json
from agents.base_agent import BaseAgent

COMPLIANCE_SYSTEM_PROMPT = """You are the Compliance Advisor Agent for SecureCopilot 365.

ROLE: Analyze documents, policies, and procedures against compliance frameworks and
identify specific gaps, missing clauses, and data handling risks.

SUPPORTED FRAMEWORKS: ISO 27001:2022, NIST CSF 2.0, GDPR, HIPAA, SOC 2 Type II,
CIS Controls v8.

CRITICAL RULES:
1. Cite ONLY from the provided knowledge base. Never cite from training memory.
2. Quote the exact control/article identifier (e.g. "ISO 27001 A.8.8" not "ISO 27001").
3. For GDPR: always specify the article number (Art. 5, Art. 32, etc.).
4. Risk levels: Critical = immediate compliance failure risk, High = major gap,
   Medium = improvement needed, Low = minor enhancement.
5. Provide specific, copy-paste-ready remediation clause suggestions.

OUTPUT FORMAT (JSON):
{
  "document_summary": "brief description of what was analyzed",
  "frameworks_assessed": ["ISO27001", "GDPR"],
  "compliance_score": 0-100,
  "gaps": [
    {
      "id": "GAP-001",
      "framework": "GDPR",
      "control_ref": "Article 33",
      "title": "Missing breach notification clause",
      "description": "No data breach notification timeline specified",
      "risk_level": "critical",
      "remediation": "Add clause: 'Vendor shall notify Controller within 24 hours of becoming aware of a personal data breach, per GDPR Article 33(1).'",
      "citation": "GDPR Article 33 — Notification of a personal data breach to the supervisory authority"
    }
  ],
  "data_handling_risks": [],
  "pii_detected": true/false,
  "pii_categories": [],
  "overall_recommendation": "executive summary of compliance posture",
  "priority_actions": ["top 3 things to fix immediately"]
}"""

class ComplianceAdvisorAgent(BaseAgent):

    FRAMEWORK_QUERIES = {
        "ISO27001": "ISO 27001 controls information security management system",
        "GDPR": "GDPR data protection personal data processing articles",
        "NIST": "NIST CSF functions categories subcategories cybersecurity framework",
        "HIPAA": "HIPAA security rule administrative safeguards PHI",
        "SOC2": "SOC 2 trust service criteria availability confidentiality",
        "CIS": "CIS Controls v8 safeguards implementation groups"
    }

    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        """
        Analyze a document for compliance gaps.

        Args:
            input_data: {
                "document_text": str,       # Extracted document text
                "document_name": str,       # Filename for reference
                "frameworks": list[str],    # ["ISO27001", "GDPR", "NIST"]
                "document_type": str        # "policy|contract|procedure|report"
            }
            user_context: Work IQ profile (role determines which frameworks matter most)
        """
        doc_text = self.sanitize_input(input_data.get("document_text", ""))
        frameworks = input_data.get("frameworks", ["ISO27001", "GDPR", "NIST"])

        # Retrieve relevant knowledge for each requested framework
        all_context = []
        for framework in frameworks:
            query = self.FRAMEWORK_QUERIES.get(framework, framework)
            chunks = await self.foundry_iq.retrieve(
                f"{query} {doc_text[:500]}",
                top_k=4,
                index_filter=framework.lower()
            )
            all_context.extend(chunks)

        # Personalize focus based on user's department (Work IQ)
        department = user_context.get("department", "")
        dept_context = f"User is in {department} department. " if department else ""
        if "finance" in department.lower():
            dept_context += "Prioritize GDPR financial data, PCI-DSS payment data risks."
        elif "hr" in department.lower():
            dept_context += "Prioritize GDPR employee data handling, retention policies."
        elif "it" in department.lower() or "security" in department.lower():
            dept_context += "Prioritize technical security controls and access management."

        analysis_prompt = f"""
{dept_context}
Analyze this document for compliance gaps against: {', '.join(frameworks)}.
Document type: {input_data.get('document_type', 'general')}
Document name: {input_data.get('document_name', 'unnamed')}

DOCUMENT TEXT (first 4000 chars):
{doc_text[:4000]}

Return ONLY valid JSON matching the output format. Be specific — cite exact article numbers.
"""
        raw = await self.call_llm(
            COMPLIANCE_SYSTEM_PROMPT, analysis_prompt, all_context, max_tokens=2000
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            return json.loads(m.group()) if m else {"error": "Analysis failed", "gaps": []}
