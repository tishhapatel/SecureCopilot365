"""
Base Agent — shared functionality for all SecureCopilot 365 agents.
Handles: Azure OpenAI calls, Foundry IQ RAG retrieval, citation formatting,
         prompt injection sanitization, response structuring.
"""
from abc import ABC, abstractmethod
from openai import AsyncAzureOpenAI
from typing import Any
import logging, re, json, os
from iq.foundry_iq import FoundryIQ
from iq.work_iq import WorkIQ

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if self.api_key and self.endpoint:
            try:
                self.client = AsyncAzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Running in Mock mode.")
                self.client = None
        else:
            logger.info("Azure OpenAI credentials not configured. Running in Mock mode.")
            self.client = None
            
        self.foundry_iq = FoundryIQ()
        self.work_iq = WorkIQ()

    def sanitize_input(self, user_input: str) -> str:
        """
        Prompt injection protection.
        Strips patterns that attempt to override system instructions.
        This is CRITICAL for the Phishing Detection Agent where email
        content is passed as user input and could contain injection attacks.
        """
        injection_patterns = [
            r"ignore (previous|all|above) instructions",
            r"system:\s",
            r"you are now",
            r"new instructions:",
            r"forget everything",
            r"<\|system\|>",
            r"<\|user\|>",
            r"\[INST\]",
            r"###\s*(System|Instruction)",
        ]
        sanitized = user_input
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        # Limit input length to prevent token stuffing attacks
        return sanitized[:8000]

    async def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        context_chunks: list[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.1
    ) -> str:
        """
        Core LLM call with RAG context injection.
        Enforces Explainable AI JSON schema output formatting constraints while maintaining backwards compatibility.
        Low temperature (0.1) ensures consistent, factual security analysis.
        If Azure OpenAI is not configured, generates a simulated output based on the agent type.
        """
        # Append Explainable AI formatting instructions to the system prompt
        explainability_instruction = (
            "\n\nCRITICAL: You MUST output your response strictly as a JSON object matching the following schema. "
            "You MUST include all fields, combining both new Explainable AI keys and legacy attributes for compatibility:\n"
            "{\n"
            '  "finding": "Summary verdict of the analysis",\n'
            '  "reasoning": "Step-by-step description of how you derived the verdict.",\n'
            '  "evidence": [\n'
            "    {\n"
            '      "source": "Document name, email sender, or API endpoint source",\n'
            '      "extract": "Direct text snippet or telemetry value supporting finding",\n'
            '      "reliability": "high | medium | low"\n'
            "    }\n"
            "  ],\n"
            '  "sources": ["Citations, regulatory clauses, or framework identifiers (e.g. ISO 27001 Annex A.8.24)"],\n'
            '  "confidence_score": 0.0-1.0,\n'
            '  "recommended_action": "Actionable next steps to address the finding.",\n'
            '  "risk_score": 0-100,\n'
            '  "risk_level": "low | medium | high | critical",\n'
            '  "verdict": "phishing | bec_attempt | safe" (only for phishing agent),\n'
            '  "indicators": [] (only for phishing agent),\n'
            '  "compliance_score": 0-100 (only for compliance advisor),\n'
            '  "gaps": [] (only for compliance advisor),\n'
            '  "pii_detected": true | false (only for compliance advisor),\n'
            '  "findings": [] (only for vendor risk agent),\n'
            '  "risk_tier": "low | medium | high" (only for vendor risk agent),\n'
            '  "overall_readiness_score": 0-100 (only for audit readiness agent),\n'
            '  "controls_summary": {} (only for audit readiness agent),\n'
            '  "critical_gaps": [] (only for audit readiness agent),\n'
            '  "interactive_scenario": {} (only for security awareness coach),\n'
            '  "quiz": {} (only for security awareness coach)\n'
            "}"
        )
        
        # Don't apply formatting schema to the Master Orchestrator, which has its own routing format
        effective_system_prompt = system_prompt
        if "Master Orchestrator" not in system_prompt:
            effective_system_prompt += explainability_instruction

        if self.client is not None:
            messages = [{"role": "system", "content": effective_system_prompt}]
            if context_chunks:
                context_text = "\n\n---\n\n".join(context_chunks)
                messages.append({
                    "role": "system",
                    "content": f"KNOWLEDGE BASE CONTEXT (use ONLY this for citations):\n\n{context_text}"
                })
            messages.append({"role": "user", "content": user_message})
            try:
                response = await self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object" if "Master Orchestrator" not in system_prompt else "text"}
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"LLM call failed: {e}. Falling back to mock generator.")
        
        # Mock responses generator for development/demonstration
        return self._generate_mock_response(effective_system_prompt, user_message)

    def _generate_mock_response(self, system_prompt: str, user_message: str) -> str:
        """Generates realistic mock agent responses adhering to the Explainable AI format."""
        
        # 1. Phishing Detection Agent Mock
        if "Phishing Detection Agent" in system_prompt:
            score = 92 if ("invoice" in user_message.lower() or "wire" in user_message.lower() or "password has expired" in user_message.lower()) else 12
            verdict = "bec_attempt" if score > 50 else "safe"
            
            if verdict == "bec_attempt":
                return json.dumps({
                    "finding": f"Phishing/BEC Attempt Detected (Risk Score: {score}/100 - CRITICAL)",
                    "reasoning": "The email represents a Business Email Compromise (BEC) attempt impersonating the CFO from a Gmail domain requesting an urgent wire transfer.",
                    "evidence": [
                        {
                            "source": "email_sender",
                            "extract": "external.cfo.office@gmail.com",
                            "reliability": "high"
                        },
                        {
                            "source": "email_body",
                            "extract": "verify these updated bank routing numbers... processed in 2 hours to avoid penalty fees",
                            "reliability": "high"
                        }
                    ],
                    "sources": [
                        "MITRE ATT&CK T1566.002 - Spearphishing Link",
                        "MITRE ATT&CK T1598 - Social Engineering",
                        "NIST CSF PR.AT-1 - Security Awareness"
                    ],
                    "confidence_score": 0.95,
                    "recommended_action": "Block the sender domain, report the email to SOC immediately, and alert the finance department of the spoofing attempt.",
                    "risk_score": score,
                    "risk_level": "critical",
                    "verdict": verdict,
                    "summary": "Urgent wire transfer request impersonating financial authority.",
                    "indicators": [
                        {
                            "category": "Social Engineering",
                            "description": "Urgent language requesting sensitive financial transactions was detected.",
                            "severity": "high",
                            "mitre_technique": "T1598 — Social Engineering"
                        }
                    ],
                    "mitre_techniques": ["T1566.002", "T1598"],
                    "report_to_soc": True,
                    "citations": ["MITRE ATT&CK T1566.002", "NIST PR.AT-1"]
                }, indent=2)
            else:
                return json.dumps({
                    "finding": "Communication Assessed as Safe (Risk Score: 12/100)",
                    "reasoning": "No threat indicators, urgency markers, or sender reputation anomalies were detected in the analyzed message context.",
                    "evidence": [
                        {
                            "source": "email_sender",
                            "extract": "secops@enterprise.com",
                            "reliability": "high"
                        }
                    ],
                    "sources": [
                        "NIST CSF PR.AT-1 - Security Awareness"
                    ],
                    "confidence_score": 0.90,
                    "recommended_action": "Safe to proceed with normal communications.",
                    "risk_score": 12,
                    "risk_level": "low",
                    "verdict": "safe",
                    "summary": "Safe communication.",
                    "indicators": [],
                    "mitre_techniques": [],
                    "report_to_soc": False,
                    "citations": []
                }, indent=2)

        # 2. Compliance Advisor Agent Mock
        elif "Compliance Advisor Agent" in system_prompt:
            return json.dumps({
                "finding": "Compliance Gap Identified (Compliance Score: 68/100)",
                "reasoning": "The uploaded Information Security Policy draft lacks a data breach notification clause required by GDPR Article 33 and cryptography standards details required by ISO 27001 Annex A.8.24.",
                "evidence": [
                    {
                        "source": "Information_Security_Policy_Draft.docx",
                        "extract": "No breach notification timeline or cryptographic rules defined.",
                        "reliability": "high"
                    }
                ],
                "sources": [
                    "GDPR Article 33 - Notification of personal data breach",
                    "ISO 27001 A.8.24 - Use of cryptography"
                ],
                "confidence_score": 0.88,
                "recommended_action": "Insert GDPR compliance clause: 'Vendor shall notify Controller within 24 hours of becoming aware of a personal data breach' and specify AES-256 standard encryption for all data at rest.",
                "document_summary": "Corporate Information Security Policy draft",
                "frameworks_assessed": ["ISO27001", "GDPR"],
                "compliance_score": 68,
                "gaps": [
                    {
                        "id": "GAP-001",
                        "framework": "GDPR",
                        "control_ref": "Article 33",
                        "title": "Missing breach notification clause",
                        "description": "No data breach notification timeline specified in the document text.",
                        "risk_level": "critical",
                        "remediation": "Add clause: 'Vendor shall notify Controller within 24 hours of becoming aware of a personal data breach, per GDPR Article 33(1).'",
                        "citation": "GDPR Article 33 — Notification of a personal data breach to the supervisory authority"
                    }
                ],
                "data_handling_risks": ["GDPR breach risk due to missing notification timeline"],
                "pii_detected": True,
                "pii_categories": ["email", "name"],
                "overall_recommendation": "The policy meets baseline security rules but lacks critical operational definitions for GDPR and encryption rules.",
                "priority_actions": ["Add the GDPR Article 33 notification clause", "Include details on cryptography standards"]
            }, indent=2)

        # 3. Vendor Risk Agent Mock
        elif "Vendor Risk Agent" in system_prompt:
            return json.dumps({
                "finding": "Vendor Risk Rating: HIGH (Risk Score: 58/100)",
                "reasoning": "Vendor processes customer PII but lacks SOC 2 Type II certification, exposing the organization to compliance risks.",
                "evidence": [
                    {
                        "source": "vendor_profile",
                        "extract": "SOC 2 Type II: False, PII data accessed: True",
                        "reliability": "high"
                    }
                ],
                "sources": [
                    "ISO 27001 A.5.19 - Supplier relationships",
                    "GDPR Article 28 - Processor compliance requirements"
                ],
                "confidence_score": 0.91,
                "recommended_action": "Request SOC 2 Type II report or require the vendor to sign a specific Data Processing Addendum (DPA) with audit rights.",
                "vendor_name": "SaaS Platform Corp",
                "risk_score": 58,
                "risk_tier": "medium",
                "risk_summary": "Vendor processes PII but lacks a SOC 2 Type II certification. DPA is in place, and pen tests are up to date.",
                "dimension_scores": {
                    "certifications": {"score": 40, "details": "Lacks SOC 2 Type II report. Has ISO 27001 certificate."},
                    "data_access": {"score": 70, "details": "Accesses customer contact list and billing names."},
                    "questionnaire": {"score": 65, "details": "Self-attested controls are compliant, but not verified by audit."},
                    "pen_testing": {"score": 85, "details": "Penetration test report is recent (6 months ago) with all high-severity items fixed."},
                    "incident_history": {"score": 90, "details": "No recorded data breaches in the last 3 years."},
                    "sub_processors": {"score": 50, "details": "Relies on fourth-party subcontractors for hosting."}
                },
                "findings": [
                    {
                        "severity": "high",
                        "finding": "Missing SOC 2 Type II report",
                        "recommendation": "Require the vendor to provide their latest SOC 2 report or submit to a security audit.",
                        "citation": "ISO 27001 A.5.19 — Supplier relationships"
                    }
                ],
                "required_actions_before_approval": ["Request SOC 2 Type II report", "Sign updated Data Processing Agreement (DPA)"],
                "approved_alternative_vendors": ["SecureStore Inc", "DataStorage Ltd"],
                "reassessment_due": "Reassessment due annually in June."
            }, indent=2)

        # 4. Audit Readiness Agent Mock
        elif "Audit Readiness Agent" in system_prompt:
            return json.dumps({
                "finding": "ISO 27001 Audit Readiness Score: 74/100 (MOSTLY READY)",
                "reasoning": "Baseline controls are mapped, but a critical gap is identified in Control A.8.8 due to missing vulnerability scanning evidence.",
                "evidence": [
                    {
                        "source": "SharePoint / compliance-evidence",
                        "extract": "No quarterly vulnerability scan reports found.",
                        "reliability": "high"
                    }
                ],
                "sources": [
                    "ISO 27001 A.8.8 - Management of technical vulnerabilities"
                ],
                "confidence_score": 0.93,
                "recommended_action": "Configure Qualys/Nessus automated scanning reports to sync and upload to the compliance folder.",
                "framework": "ISO27001",
                "overall_readiness_score": 74,
                "readiness_band": "mostly_ready",
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
                        "gap_description": "No quarterly vulnerability scan reports found in SharePoint.",
                        "evidence_needed": "Vulnerability scan reports from approved scanning tool.",
                        "risk_if_unaddressed": "Auditor will flag as a major nonconformity.",
                        "days_to_remediate": 14,
                        "responsible_team": "IT Security"
                    }
                ],
                "collected_evidence": [
                    {
                        "control_ref": "A.5.15",
                        "evidence_type": "Entra ID RBAC Report",
                        "source": "Microsoft Entra ID",
                        "retrieved_at": "2026-06-07T12:00:00Z",
                        "status": "sufficient"
                    }
                ],
                "executive_summary": "The organization is mostly ready for an ISO 27001 audit. Main gaps relate to regular vulnerability scanning evidence and missing data backup logs in SharePoint.",
                "next_steps": ["Upload latest vulnerability scan report", "Configure Azure Backup logs integration"],
                "estimated_readiness_date": "2026-07-15"
            }, indent=2)

        # 5. Security Awareness Coach Agent Mock
        elif "Security Awareness Coach Agent" in system_prompt:
            return json.dumps({
                "finding": "Security Quiz: Business Email Compromise (BEC)",
                "reasoning": "Interactive training scenario to educate billing specialists on wire transfer scam emails and CEO impersonation.",
                "evidence": [
                    {
                        "source": "awareness_module",
                        "extract": "Role-relevance: Finance Specialists",
                        "reliability": "high"
                    }
                ],
                "sources": [
                    "ISO 27001 A.6.3 - Information security awareness, education and training",
                    "NIST CSF PR.AT-1 - Awareness training"
                ],
                "confidence_score": 0.95,
                "recommended_action": "Explain the scenario where CEO/CFO requests a transfer, and test the user with standard email-checking options.",
                "topic": "Business Email Compromise (BEC)",
                "learning_objective": "Identify wire transfer scam emails and CEO impersonation attempts.",
                "role_relevance": "High relevance for finance departments and billing managers.",
                "interactive_scenario": {
                    "scenario_id": "TC-001",
                    "intro": "You receive an email from 'CFO Display Name <cfo.company.executive@gmail.com>' marked URGENT.",
                    "question": "The email asks you to update payment details for a pending contractor invoice immediately to prevent late fees. What is your first action?",
                    "options": [
                        "Reply immediately requesting the contract copy.",
                        "Change the bank details in the billing system and initiate the wire transfer.",
                        "Verify the sender's actual email address, spot the Gmail domain, and report the email via the SecureCopilot Outlook add-in.",
                        "Ignore the email completely."
                    ],
                    "correct_option_index": 2,
                    "explanation": "CEO/CFO impersonation scams commonly use free email accounts (like Gmail) with mismatched display names. Always verify out-of-band and report using SecureCopilot."
                },
                "quiz": {
                    "question": "You receive an email from 'CFO Display Name <cfo.company.executive@gmail.com>' marked URGENT.",
                    "options": [
                        "Reply immediately requesting the contract copy.",
                        "Change the bank details in the billing system and initiate the wire transfer.",
                        "Verify the sender's actual email address, spot the Gmail domain, and report the email via the SecureCopilot Outlook add-in.",
                        "Ignore the email completely."
                    ],
                    "correct_option_index": 2,
                    "explanation": "CEO/CFO impersonation scams commonly use free email accounts (like Gmail) with mismatched display names. Always verify out-of-band and report using SecureCopilot."
                },
                "key_takeaway": "Never make bank account modifications based solely on email instructions. Always verify through a phone call or official internal channel."
            }, indent=2)

        # 6. Master Orchestrator Agent Mock
        else:
            return json.dumps({
                "selected_agent": "phishing",
                "confidence": 0.95,
                "routing_rationale": "Request asks to scan an email for threat indicators.",
                "redirect_suggested": None
            })



    @abstractmethod
    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        """Each agent implements its specific analysis logic."""
        pass
