from typing import List, Dict, Any
from datetime import datetime

def calculate_phishing_risk_score(indicators: List[Dict[str, Any]]) -> float:
    """
    Calculate risk score based on rule-based indicators.
    Scores: Critical (+45), High (+25), Medium (+10), Low (+5)
    Maximum score is capped at 100.
    """
    if not indicators:
        return 0.0
        
    score = 0.0
    for ind in indicators:
        severity = ind.get("severity", "low").lower()
        if severity == "critical":
            score += 45.0
        elif severity == "high":
            score += 25.0
        elif severity == "medium":
            score += 10.0
        else:
            score += 5.0
            
    return min(100.0, score)

def calculate_vendor_risk_score(
    cert_score: float,
    data_score: float,
    questionnaire_responses: Dict[str, Any],
    pen_test_date_str: str,
    incidents: List[Dict[str, Any]],
    dpa_signed: bool
) -> float:
    """
    TPRM Risk Scoring Engine.
    Calculates vendor risk score (0-100) using weighted dimensions:
    - Certifications: 25% (cert_score)
    - Data sensitivity: 20% (data_score)
    - Questionnaire response: 20%
    - Pen test recency: 15%
    - Incident history: 10%
    - DPA compliance: 10%
    """
    # 1. Questionnaire score (default to 50 if empty)
    q_score = 50.0
    if questionnaire_responses:
        yes_count = 0
        total_questions = len(questionnaire_responses)
        if total_questions > 0:
            for q, val in questionnaire_responses.items():
                if val is True or str(val).lower() in ["yes", "true"]:
                    yes_count += 1
            q_score = (yes_count / total_questions) * 100.0
    # Map q_score from compliance/adherence (higher is better) to RISK (lower is better)
    q_risk = 100.0 - q_score

    # 2. Pen test recency
    pen_test_risk = 80.0 # Default high risk if no pen test
    if pen_test_date_str:
        try:
            pen_test_date = datetime.strptime(pen_test_date_str[:10], "%Y-%m-%d")
            days_since = (datetime.utcnow() - pen_test_date).days
            if days_since < 180:
                pen_test_risk = 0.0  # Safe
            elif days_since < 365:
                pen_test_risk = 30.0 # Medium risk
            else:
                pen_test_risk = 60.0 # High risk
        except (ValueError, TypeError):
            pen_test_risk = 80.0 # Default high risk on invalid date format

    # 3. Incident history
    incident_risk = 0.0
    if incidents:
        # Scale risk based on quantity and severity of incidents
        incident_risk = min(100.0, len(incidents) * 35.0)

    # 4. DPA Compliance risk
    dpa_risk = 0.0 if dpa_signed else 80.0

    # Cert score is compliance rating. Convert to risk.
    cert_risk = 100.0 - cert_score

    # Weighted sum
    weighted_score = (
        (cert_risk * 0.25) +
        (data_score * 0.20) +
        (q_risk * 0.20) +
        (pen_test_risk * 0.15) +
        (incident_risk * 0.10) +
        (dpa_risk * 0.10)
    )

    return round(max(0.0, min(100.0, weighted_score)), 1)
