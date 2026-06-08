"""
Vendor Risk Agent — Third-Party Risk Management (TPRM)
Scores vendors across security certifications, questionnaire responses,
data access scope, incident history, and sub-processor risk.
Deployed in: Teams, SharePoint, Copilot Chat.

Risk dimensions scored (weighted):
1. Security certifications (ISO 27001, SOC 2 Type II, CSA STAR) — 25%
2. Data access scope and sensitivity — 20%
3. Questionnaire response completeness and quality — 20%
4. Penetration testing recency — 15%
5. Incident history and disclosure transparency — 10%
6. Sub-processor and fourth-party risk — 10%
"""
import json
from agents.base_agent import BaseAgent
from utils.scoring import calculate_vendor_risk_score

VENDOR_SYSTEM_PROMPT = """You are the Vendor Risk Agent for SecureCopilot 365.

ROLE: Assess third-party vendor security posture using TPRM best practices aligned to
ISO 27001 Annex A.5.19 (Information security in supplier relationships), CIS Control 15,
and NIST CSF GV.SC (Supply Chain Risk Management).

OUTPUT FORMAT (JSON):
{
  "vendor_name": "name",
  "risk_score": 0-100,
  "risk_tier": "critical|high|medium|low",
  "risk_summary": "2-sentence executive summary",
  "dimension_scores": {
    "certifications": {"score": 0-100, "details": ""},
    "data_access": {"score": 0-100, "details": ""},
    "questionnaire": {"score": 0-100, "details": ""},
    "pen_testing": {"score": 0-100, "details": ""},
    "incident_history": {"score": 0-100, "details": ""},
    "sub_processors": {"score": 0-100, "details": ""}
  },
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "finding": "specific issue found",
      "recommendation": "specific remediation action",
      "citation": "ISO 27001 A.5.19 or relevant standard"
    }
  ],
  "required_actions_before_approval": [],
  "approved_alternative_vendors": [],
  "reassessment_due": "ISO 27001 requires annual reassessment for high-risk vendors"
}"""

class VendorRiskAgent(BaseAgent):

    CERTIFICATION_WEIGHTS = {
        "iso27001": 30,
        "soc2_type2": 30,
        "soc2_type1": 15,
        "csa_star": 15,
        "iso27017": 10,
        "pci_dss": 20,  # if relevant
    }

    DATA_SENSITIVITY_WEIGHTS = {
        "personal_data_pii": 30,
        "financial_data": 25,
        "health_data_phi": 35,
        "intellectual_property": 20,
        "credentials_secrets": 40,
        "employee_data": 25,
        "public_data_only": 5,
    }

    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        """
        Score a vendor's risk profile.

        Args:
            input_data: {
                "vendor_name": str,
                "vendor_website": str,
                "data_categories": list[str],      # what data the vendor accesses
                "certifications": dict,             # {iso27001: true, soc2_type2: false}
                "questionnaire_responses": dict,    # completed security questionnaire
                "pen_test_date": str,               # YYYY-MM-DD or null
                "sub_processors": list[str],        # disclosed sub-processors
                "incident_history": list[dict],     # known incidents
                "dpa_signed": bool,                 # Data Processing Agreement
                "contract_sla": str                 # relevant security SLA text
            }
        """
        # Rule-based pre-scoring for certifications and data sensitivity
        cert_score = self._score_certifications(input_data.get("certifications", {}))
        data_score = self._score_data_sensitivity(input_data.get("data_categories", []))

        # Retrieve TPRM context from Foundry IQ
        context = await self.foundry_iq.retrieve(
            f"vendor risk third party TPRM {input_data.get('vendor_name', '')} supply chain",
            top_k=5, index_filter="iso27001"
        )

        analysis_prompt = f"""
Assess vendor: {input_data.get('vendor_name')}
Website: {input_data.get('vendor_website', 'not provided')}
Data accessed: {json.dumps(input_data.get('data_categories', []))}
Certifications: {json.dumps(input_data.get('certifications', {}))}
Pen test date: {input_data.get('pen_test_date', 'not provided')}
Sub-processors: {json.dumps(input_data.get('sub_processors', []))}
Incident history: {json.dumps(input_data.get('incident_history', []))}
DPA signed: {input_data.get('dpa_signed', False)}
Rule-based pre-scores: certifications={cert_score:.0f}/100, data_sensitivity_risk={data_score:.0f}/100

Questionnaire responses: {json.dumps(input_data.get('questionnaire_responses', {}))[:2000]}

Return ONLY valid JSON. The risk_score should be a weighted combination of all dimensions.
"""
        raw = await self.call_llm(VENDOR_SYSTEM_PROMPT, analysis_prompt, context, max_tokens=1800)
        try:
            result = json.loads(raw)
            result["dimension_scores"]["certifications"]["score"] = cert_score
            # Fill missing dimension scores if LLM outputs an incomplete dictionary
            for dim in ["data_access", "questionnaire", "pen_testing", "incident_history", "sub_processors"]:
                if dim not in result["dimension_scores"]:
                    result["dimension_scores"][dim] = {"score": 50.0, "details": "Estimated"}
            return result
        except:
            # Reconstruct risk score using the python math algorithm if JSON decode fails
            fallback_score = calculate_vendor_risk_score(
                cert_score=cert_score,
                data_score=data_score,
                questionnaire_responses=input_data.get("questionnaire_responses", {}),
                pen_test_date_str=input_data.get("pen_test_date", ""),
                incidents=input_data.get("incident_history", []),
                dpa_signed=input_data.get("dpa_signed", False)
            )
            return {
                "vendor_name": input_data.get("vendor_name"),
                "risk_score": fallback_score,
                "risk_tier": "critical" if fallback_score >= 80 else "high" if fallback_score >= 60 else "medium" if fallback_score >= 30 else "low",
                "risk_summary": "Automated TPRM evaluation score calculated via mathematical rules.",
                "dimension_scores": {
                    "certifications": {"score": cert_score, "details": "Evaluated based on certificates"},
                    "data_access": {"score": data_score, "details": "Risk of accessed categories"},
                    "questionnaire": {"score": 50, "details": "Self-assessment checklist"},
                    "pen_testing": {"score": 50, "details": "Audit history checks"},
                    "incident_history": {"score": 0, "details": "Disclosed events"},
                    "sub_processors": {"score": 50, "details": "Supply chain visibility"}
                },
                "findings": [
                    {
                        "severity": "high" if fallback_score >= 60 else "medium",
                        "finding": "Automated rules fallback triggered",
                        "recommendation": "Request a manual security architecture review.",
                        "citation": "ISO 27001 A.5.19"
                    }
                ],
                "required_actions_before_approval": ["Verify security questionnaire documentation"],
                "approved_alternative_vendors": [],
                "reassessment_due": "Reassessment due in 12 months."
            }

    def _score_certifications(self, certs: dict) -> float:
        if not certs:
            return 0.0  # Lacks all certifications
        score = 0.0
        for cert, has_it in certs.items():
            if has_it and cert in self.CERTIFICATION_WEIGHTS:
                score += self.CERTIFICATION_WEIGHTS[cert]
        return min(100.0, score)

    def _score_data_sensitivity(self, categories: list) -> float:
        if not categories:
            return 20.0
        max_weight = max((self.DATA_SENSITIVITY_WEIGHTS.get(c, 10) for c in categories), default=10)
        return min(100.0, max_weight * 1.5)
