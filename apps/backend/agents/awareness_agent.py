"""
Security Awareness Coach Agent
Delivers personalized security training based on employee role and department.
Deployed in: Teams, Copilot Chat.

Personalization via Work IQ:
- Finance → BEC, wire fraud, invoice manipulation, CFO impersonation
- HR → employee data GDPR, employee screening, secure offboarding
- IT/Engineering → OWASP Top 10, prompt injection, secure coding, access control
- Sales/Marketing → social engineering, credential phishing, leaks
"""
import json
from agents.base_agent import BaseAgent

AWARENESS_SYSTEM_PROMPT = """You are the Security Awareness Coach Agent for SecureCopilot 365.

ROLE: Deliver personalized, engaging, and department-specific security training to employees.
Generate interactive scenarios to test employee awareness and explain best practices.

PERSONALIZATION RULE (based on Department):
- Finance: Focus on BEC (Business Email Compromise), wire transfer scams, vendor account modifications, invoice fraud.
- HR: Focus on personal data privacy (GDPR, HIPAA), credential phishing, social engineering via resume attachments.
- IT / Engineering: Focus on secure development (OWASP Top 10), prompt injection, API key leaks, access control.
- Other / General: Focus on basic hygiene (strong passwords, MFA, spotting phishing links, reporting procedures).

OUTPUT FORMAT (JSON):
{
  "topic": "topic name",
  "learning_objective": "brief statement of what is taught",
  "role_relevance": "why this is critical for this specific role/department",
  "interactive_scenario": {
    "scenario_id": "SC-00x",
    "intro": "contextual setup of a security dilemma",
    "question": "what is the best security-minded action to take?",
    "options": [
      "Option A (incorrect or partially correct)",
      "Option B (correct and recommended)",
      "Option C (incorrect)",
      "Option D (incorrect)"
    ],
    "correct_option_index": 1,
    "explanation": "detailed reasoning behind the correct choice"
  },
  "key_takeaway": "one sentence summarizing the best practice",
  "citations": ["ISO 27001 A.6.3", "NIST CSF PR.AT-1"]
}"""

class SecurityAwarenessCoach(BaseAgent):
    async def analyze(self, input_data: dict, user_context: dict) -> dict:
        """
        Generate a personalized security training scenario.

        Args:
            input_data: {
                "topic": str,               # Optional topic request
                "level": str                # beginner|intermediate|advanced
            }
            user_context: Work IQ user profile containing department and job_title
        """
        department = user_context.get("department", "General").lower()
        job_title = user_context.get("job_title", "Employee")
        
        # Select default topics if not provided
        default_topic = "Security Hygiene"
        if "finance" in department or "billing" in department:
            default_topic = "Business Email Compromise & Wire Scams"
        elif "hr" in department or "resource" in department:
            default_topic = "GDPR Employee Data Protection"
        elif "it" in department or "engineer" in department or "developer" in department:
            default_topic = "OWASP Top 10 & API Secret Management"
        elif "sales" in department or "marketing" in department:
            default_topic = "Credential Phishing & Social Engineering"

        requested_topic = input_data.get("topic") or default_topic
        level = input_data.get("level", "intermediate")

        # Retrieve education guidance from knowledge base
        context = await self.foundry_iq.retrieve(
            f"security awareness training {requested_topic} {level}",
            top_k=4, index_filter="iso27001"
        )

        analysis_prompt = f"""
Generate a training scenario.
User Department: {department.capitalize()}
User Job Title: {job_title}
Requested Topic: {requested_topic}
Difficulty Level: {level}

Tailor the scenario specifically to their day-to-day job duties.
Return ONLY valid JSON matching the specified format. No markdown, no prose.
"""
        raw = await self.call_llm(
            AWARENESS_SYSTEM_PROMPT, analysis_prompt, context, max_tokens=1800
        )
        try:
            return json.loads(raw)
        except:
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            return json.loads(m.group()) if m else self._fallback_training(requested_topic)

    def _fallback_training(self, topic: str) -> dict:
        return {
            "topic": topic,
            "learning_objective": "Identify security threat signals.",
            "role_relevance": "Critical for protecting corporate resources.",
            "interactive_scenario": {
                "scenario_id": "SC-FALLBACK",
                "intro": "You suspect a phishing attempt on a company portal.",
                "question": "What is the correct protocol?",
                "options": [
                    "Ignore it",
                    "Click verify to check",
                    "Report immediately to the security team",
                    "Forward to colleagues to warn them"
                ],
                "correct_option_index": 2,
                "explanation": "Reporting ensures the security team can block the domain immediately."
            },
            "key_takeaway": "Always report anomalies via the official channels.",
            "citations": ["ISO 27001 A.6.3"]
        }
