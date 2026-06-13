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
        # Seed Roles and Permissions first
        logger.info("Seeding Roles and Permissions...")
        from auth.roles import ALL_ROLES
        from auth.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
        from auth.jwt_handler import hash_password
        
        # Seed permissions
        permission_map = {}
        for perm in ALL_PERMISSIONS:
            db_perm = db.query(models.Permission).filter(models.Permission.permission_name == perm["name"]).first()
            if not db_perm:
                db_perm = models.Permission(permission_name=perm["name"], module=perm["module"])
                db.add(db_perm)
                db.flush()
            permission_map[perm["name"]] = db_perm
            
        # Seed roles
        role_map = {}
        for r_name in ALL_ROLES:
            db_role = db.query(models.Role).filter(models.Role.role_name == r_name).first()
            if not db_role:
                db_role = models.Role(role_name=r_name, description=f"{r_name} system role")
                db.add(db_role)
                db.flush()
            role_map[r_name] = db_role
            
            # Map permissions to roles
            target_perms = ROLE_PERMISSIONS.get(r_name, [])
            db_role.permissions = [permission_map[p] for p in target_perms if p in permission_map]
        db.commit()

        # Seed Default Users
        logger.info("Seeding Default Users...")
        default_users = [
            ("superadmin@securecop.com", "Super Admin User", "Super Admin", "IT", "tenant-alpha"),
            ("ciso@securecop.com", "CISO User", "CISO", "Security", "tenant-alpha"),
            ("auditor@securecop.com", "Auditor User", "Security Auditor", "Compliance", "tenant-alpha"),
            ("hr@securecop.com", "HR User", "HR Manager", "Human Resources", "tenant-alpha"),
            ("compliance@securecop.com", "Compliance User", "Compliance Officer", "Compliance", "tenant-alpha"),
            ("vendor@securecop.com", "Vendor User", "Vendor Risk Manager", "Procurement", "tenant-alpha"),
            ("employee@securecop.com", "Employee User", "General Employee", "Finance", "tenant-alpha"),
            # Beta tenant users
            ("ciso.beta@securecop.com", "Beta CISO User", "CISO", "Security", "tenant-beta"),
            ("employee.beta@securecop.com", "Beta Employee User", "General Employee", "Finance", "tenant-beta")
        ]
        
        for email, name, role_name, dept, tenant in default_users:
            db_user = db.query(models.User).filter(models.User.email == email).first()
            if not db_user:
                r_obj = role_map[role_name]
                db_user = models.User(
                    email=email,
                    display_name=name,
                    password_hash=hash_password("password123"),
                    role_id=r_obj.id,
                    department=dept,
                    tenant_id=tenant,
                    is_active=True
                )
                db.add(db_user)
        db.commit()

        # Check if telemetry already seeded
        if db.query(models.Employee).first():
            logger.info("Telemetry data already seeded.")
            return

        logger.info("Seeding Employees...")
        employees = [
            # tenant-alpha
            models.Employee(
                entra_id="mock-entra-id-123",
                display_name="Tisha Patel",
                email="tisha.patel@enterprise.com",
                department="Finance",
                job_title="Billing Specialist",
                risk_score=35.0,
                awareness_score=82.0,
                last_training_date=datetime.utcnow() - timedelta(days=5),
                tenant_id="tenant-alpha"
            ),
            models.Employee(
                entra_id="entra-id-bob",
                display_name="Bob Johnson",
                email="bob.johnson@enterprise.com",
                department="Human Resources",
                job_title="HR Manager",
                risk_score=55.0,
                awareness_score=68.0,
                last_training_date=datetime.utcnow() - timedelta(days=12),
                tenant_id="tenant-alpha"
            ),
            models.Employee(
                entra_id="entra-id-alice",
                display_name="Alice Smith",
                email="alice.smith@enterprise.com",
                department="IT Security",
                job_title="Security Analyst",
                risk_score=12.0,
                awareness_score=95.0,
                last_training_date=datetime.utcnow() - timedelta(days=2),
                tenant_id="tenant-alpha"
            ),
            models.Employee(
                entra_id="entra-id-charlie",
                display_name="Charlie Brown",
                email="charlie.brown@enterprise.com",
                department="Sales",
                job_title="Sales Executive",
                risk_score=72.0,
                awareness_score=45.0,
                last_training_date=datetime.utcnow() - timedelta(days=30),
                tenant_id="tenant-alpha"
            ),
            # tenant-beta
            models.Employee(
                entra_id="entra-id-beta-employee",
                display_name="Beta Employee",
                email="employee.beta@securecop.com",
                department="Finance",
                job_title="Billing Specialist",
                risk_score=40.0,
                awareness_score=80.0,
                last_training_date=datetime.utcnow() - timedelta(days=3),
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(employees)
        db.commit()

        # Fetch employee records for relationships
        emp_tisha = db.query(models.Employee).filter(models.Employee.email == "tisha.patel@enterprise.com").first()
        emp_charlie = db.query(models.Employee).filter(models.Employee.email == "charlie.brown@enterprise.com").first()
        emp_bob = db.query(models.Employee).filter(models.Employee.email == "bob.johnson@enterprise.com").first()
        emp_beta = db.query(models.Employee).filter(models.Employee.email == "employee.beta@securecop.com").first()

        logger.info("Seeding Phishing Incidents...")
        incidents = [
            # tenant-alpha
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
                reported_to_soc=False,
                tenant_id="tenant-alpha"
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
                reported_to_soc=True,
                tenant_id="tenant-alpha"
            ),
            # tenant-beta
            models.PhishingIncident(
                employee_id=emp_beta.id,
                email_subject="Urgent action required on your account",
                sender_domain="security-alert-beta.com",
                risk_score=90.0,
                risk_level=models.RiskLevel.CRITICAL,
                mitre_techniques=json.dumps(["T1566.002"]),
                indicators=json.dumps([
                    {"category": "Domain Spoofing", "description": "Unregistered domain sender"}
                ]),
                user_action="clicked",
                reported_to_soc=False,
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(incidents)

        logger.info("Seeding Vendors...")
        vendors = [
            # tenant-alpha
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
                notes="Low risk SaaS platform. Certificates validated.",
                tenant_id="tenant-alpha"
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
                notes="High risk CRM tool. Lacks ISO 27001 or SOC 2 certification. Missing DPA.",
                tenant_id="tenant-alpha"
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
                notes="Medium risk. Holds ISO certificate, processes non-critical marketing records.",
                tenant_id="tenant-alpha"
            ),
            # tenant-beta
            models.Vendor(
                name="BetaVendor Corp",
                website="https://betavendor.com",
                data_categories=json.dumps(["credentials_secrets"]),
                risk_score=85.0,
                risk_level=models.RiskLevel.CRITICAL,
                iso27001_certified=False,
                soc2_type2=False,
                gdpr_dpa_signed=False,
                last_assessment_date=datetime.utcnow() - timedelta(days=10),
                sub_processors=json.dumps([]),
                questionnaire_score=30.0,
                notes="Critical risk. No validation docs.",
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(vendors)

        logger.info("Seeding Compliance Gaps...")
        queries = [
            # tenant-alpha
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
                citations=json.dumps(["GDPR Article 33"]),
                tenant_id="tenant-alpha"
            ),
            # tenant-beta
            models.ComplianceQuery(
                employee_id=emp_beta.id,
                document_name="Beta_Policy.docx",
                frameworks_checked=json.dumps(["ISO27001"]),
                gaps_found=1,
                gap_details=json.dumps([
                    {
                        "id": "GAP-002",
                        "framework": "ISO27001",
                        "control_ref": "A.12.4.1",
                        "title": "Logging missing",
                        "description": "No system event logging specified",
                        "risk_level": "high",
                        "remediation": "Enable centralized logging",
                        "citation": "A.12.4.1"
                    }
                ]),
                remediation_provided=True,
                citations=json.dumps(["A.12.4.1"]),
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(queries)

        logger.info("Seeding Audit Readiness Report...")
        audits = [
            # tenant-alpha
            models.AuditReadiness(
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
                assessed_by=emp_bob.id,
                tenant_id="tenant-alpha"
            ),
            # tenant-beta
            models.AuditReadiness(
                framework="SOC2",
                overall_score=60.0,
                controls_total=50,
                controls_evidenced=30,
                controls_partial=5,
                controls_missing=15,
                critical_gaps=json.dumps([]),
                evidence_package=json.dumps([]),
                assessed_by=emp_beta.id,
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(audits)

        logger.info("Seeding Training Completion...")
        training = [
            models.TrainingCompletion(
                employee_id=emp_tisha.id,
                topic="Business Email Compromise (BEC)",
                score=100.0,
                passed=True,
                tenant_id="tenant-alpha"
            ),
            models.TrainingCompletion(
                employee_id=emp_beta.id,
                topic="Phishing 101",
                score=90.0,
                passed=True,
                tenant_id="tenant-beta"
            )
        ]
        db.add_all(training)

        db.commit()
        logger.info("Database seeded successfully.")
    except Exception as ex:
        logger.error(f"Error seeding database: {ex}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
