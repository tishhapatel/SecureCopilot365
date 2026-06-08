"""
SecureCopilot 365 — Knowledge Ingestion & Seeding Script
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Adjust path to import from backend
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "backend"))

from db.database import SessionLocal, engine
from db import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    logger.info("Initializing database tables...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Employee).first():
            logger.info("Database already seeded with values.")
            return

        logger.info("Seeding Employees...")
        employees = [
            models.Employee(
                entra_id="mock-entra-id-123",
                display_name="Tisha Patel",
                email="tisha.patel@enterprise.com",
                department="Finance",
                job_title="Billing Specialist",
                risk_score=35.0,
                awareness_score=82.0,
                last_training_date=datetime.utcnow() - timedelta(days=5)
            ),
            models.Employee(
                entra_id="entra-id-bob",
                display_name="Bob Johnson",
                email="bob.johnson@enterprise.com",
                department="Human Resources",
                job_title="HR Manager",
                risk_score=55.0,
                awareness_score=68.0,
                last_training_date=datetime.utcnow() - timedelta(days=12)
            ),
            models.Employee(
                entra_id="entra-id-alice",
                display_name="Alice Smith",
                email="alice.smith@enterprise.com",
                department="IT Security",
                job_title="Security Analyst",
                risk_score=12.0,
                awareness_score=95.0,
                last_training_date=datetime.utcnow() - timedelta(days=2)
            ),
            models.Employee(
                entra_id="entra-id-charlie",
                display_name="Charlie Brown",
                email="charlie.brown@enterprise.com",
                department="Sales",
                job_title="Sales Executive",
                risk_score=72.0,
                awareness_score=45.0,
                last_training_date=datetime.utcnow() - timedelta(days=30)
            )
        ]
        db.add_all(employees)
        db.commit()

        # Fetch employee records for relationships
        emp_tisha = db.query(models.Employee).filter(models.Employee.email == "tisha.patel@enterprise.com").first()
        emp_bob = db.query(models.Employee).filter(models.Employee.email == "bob.johnson@enterprise.com").first()
        emp_charlie = db.query(models.Employee).filter(models.Employee.email == "charlie.brown@enterprise.com").first()

        logger.info("Seeding Phishing Incidents...")
        incidents = [
            models.PhishingIncident(
                employee_id=emp_charlie.id,
                email_subject="ALERT: Your Office 365 session has expired",
                sender_domain="login-microsoft-auth.com",
                risk_score=85.0,
                risk_level=models.RiskLevel.CRITICAL,
                mitre_techniques=json.dumps(["T1566.002", "T1598"]),
                indicators=json.dumps([
                    {"category": "Domain Spoofing", "description": "Lookalike domain login-microsoft-auth.com substituted for login.microsoftonline.com"},
                    {"category": "Social Engineering", "description": "Urgency words 'expired' and 'immediate verification' detected"}
                ]),
                user_action="ignored",
                reported_to_soc=False
            ),
            models.PhishingIncident(
                employee_id=emp_tisha.id,
                email_subject="Overdue Invoice payment instructions",
                sender_domain="billing-accounts-pay-xyz.com",
                risk_score=74.0,
                risk_level=models.RiskLevel.HIGH,
                mitre_techniques=json.dumps(["T1534", "T1598"]),
                indicators=json.dumps([
                    {"category": "BEC Attempt", "description": "Requesting immediate wire transfer details alteration"},
                    {"category": "Reply-To Mismatch", "description": "Sender from billing domain but reply-to matches hacker inbox"}
                ]),
                user_action="reported",
                reported_to_soc=True
            )
        ]
        db.add_all(incidents)

        logger.info("Seeding Vendors...")
        vendors = [
            models.Vendor(
                name="CollaborationHub Inc",
                website="https://collabhub-portal.com",
                data_categories=json.dumps(["personal_data_pii", "employee_data"]),
                risk_score=38.0,
                risk_level=models.RiskLevel.LOW,
                iso27001_certified=True,
                soc2_type2=True,
                gdpr_dpa_signed=True,
                last_assessment_date=datetime.utcnow() - timedelta(days=20),
                sub_processors=json.dumps(["Amazon Web Services", "Stripe"]),
                questionnaire_score=92.0,
                notes="Low risk SaaS platform. Certificates validated."
            ),
            models.Vendor(
                name="Legacy CRM Tools",
                website="https://legacy-crm-portal.net",
                data_categories=json.dumps(["personal_data_pii", "financial_data", "credentials_secrets"]),
                risk_score=78.0,
                risk_level=models.RiskLevel.HIGH,
                iso27001_certified=False,
                soc2_type2=False,
                gdpr_dpa_signed=False,
                last_assessment_date=datetime.utcnow() - timedelta(days=60),
                sub_processors=json.dumps(["DatabaseHostingCo"]),
                questionnaire_score=45.0,
                notes="High risk CRM tool. Lacks ISO 27001 or SOC 2 certification. Missing DPA."
            ),
            models.Vendor(
                name="MarketingAnalytics Pro",
                website="https://marketing-analytics-pro.io",
                data_categories=json.dumps(["public_data_only"]),
                risk_score=52.0,
                risk_level=models.RiskLevel.MEDIUM,
                iso27001_certified=True,
                soc2_type2=False,
                gdpr_dpa_signed=True,
                last_assessment_date=datetime.utcnow() - timedelta(days=45),
                sub_processors=json.dumps([]),
                questionnaire_score=70.0,
                notes="Medium risk. Holds ISO certificate, processes non-critical marketing records."
            )
        ]
        db.add_all(vendors)

        logger.info("Seeding Compliance Gaps...")
        queries = [
            models.ComplianceQuery(
                employee_id=emp_bob.id,
                document_name="Draft_Vendor_SLA.docx",
                frameworks_checked=json.dumps(["GDPR"]),
                gaps_found=1,
                gap_details=json.dumps([
                    {
                        "id": "GAP-001",
                        "framework": "GDPR",
                        "control_ref": "Article 33",
                        "title": "Missing breach notification clause",
                        "description": "No data breach notification timeline specified",
                        "risk_level": "critical",
                        "remediation": "Add clause: 'Vendor shall notify Controller within 24 hours of becoming aware of a personal data breach, per GDPR Article 33(1).'",
                        "citation": "GDPR Article 33"
                    }
                ]),
                remediation_provided=True,
                citations=json.dumps(["GDPR Article 33"])
            )
        ]
        db.add_all(queries)

        logger.info("Seeding Audit Readiness Report...")
        audit = models.AuditReadiness(
            framework="ISO27001",
            overall_score=78.5,
            controls_total=93,
            controls_evidenced=73,
            controls_partial=10,
            controls_missing=10,
            critical_gaps=json.dumps([
                {
                    "control_ref": "A.8.8",
                    "control_name": "Management of technical vulnerabilities",
                    "gap_description": "No quarterly vulnerability scan reports found in SharePoint.",
                    "evidence_needed": "Vulnerability scan reports."
                }
            ]),
            evidence_package=json.dumps([
                {"control_ref": "A.5.15", "evidence_type": "Entra ID RBAC Report", "source": "Microsoft Entra ID", "status": "sufficient"}
            ]),
            assessed_by=emp_bob.id
        )
        db.add(audit)

        logger.info("Seeding Training Completion...")
        training = models.TrainingCompletion(
            employee_id=emp_tisha.id,
            topic="Business Email Compromise (BEC)",
            score=100.0,
            passed=True
        )
        db.add(training)

        db.commit()
        logger.info("Database seeded successfully.")
    except Exception as ex:
        logger.error(f"Error seeding database: {ex}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
