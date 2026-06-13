from sqlalchemy.orm import Session
from db import models, schemas
from datetime import datetime

# User CRUD
def get_user(db: Session, user_id: str):
    """Retrieve a system user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Retrieve a user record by email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users_by_tenant(db: Session, tenant_id: str, skip: int = 0, limit: int = 100):
    """Retrieve all users associated with a specific tenant."""
    return db.query(models.User).filter(models.User.tenant_id == tenant_id).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, tenant_id: str):
    """Create a new user with a hashed password and link to a role."""
    from auth.jwt_handler import hash_password
    db_role = db.query(models.Role).filter(models.Role.role_name == user.role_name).first()
    if not db_role:
        raise ValueError(f"Role '{user.role_name}' does not exist.")
        
    db_user = models.User(
        email=user.email,
        display_name=user.display_name,
        password_hash=hash_password(user.password) if user.password else None,
        role_id=db_role.id,
        department=user.department,
        tenant_id=tenant_id,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: str, role_name: str, tenant_id: str):
    """Update a user's role mapping (restricted to the same tenant)."""
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.tenant_id == tenant_id).first()
    if db_user:
        db_role = db.query(models.Role).filter(models.Role.role_name == role_name).first()
        if db_role:
            db_user.role_id = db_role.id
            db.commit()
            db.refresh(db_user)
    return db_user

def update_user_activation(db: Session, user_id: str, is_active: bool, tenant_id: str):
    """Activate/deactivate user profiles."""
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.tenant_id == tenant_id).first()
    if db_user:
        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str, tenant_id: str):
    """Delete a user account."""
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.tenant_id == tenant_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Employee CRUD
def get_employee(db: Session, employee_id: str, tenant_id: str = "default_tenant"):
    return db.query(models.Employee).filter(models.Employee.id == employee_id, models.Employee.tenant_id == tenant_id).first()

def get_employee_by_entra_id(db: Session, entra_id: str, tenant_id: str = "default_tenant"):
    return db.query(models.Employee).filter(models.Employee.entra_id == entra_id, models.Employee.tenant_id == tenant_id).first()

def get_employees(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.Employee).filter(models.Employee.tenant_id == tenant_id).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate, tenant_id: str = "default_tenant"):
    db_employee = models.Employee(**employee.model_dump(), tenant_id=tenant_id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee_scores(db: Session, employee_id: str, risk_score: float, awareness_score: float, tenant_id: str = "default_tenant"):
    db_employee = get_employee(db, employee_id, tenant_id)
    if db_employee:
        db_employee.risk_score = risk_score
        db_employee.awareness_score = awareness_score
        db.commit()
        db.refresh(db_employee)
    return db_employee

# Vendor CRUD
def get_vendor(db: Session, vendor_id: str, tenant_id: str = "default_tenant"):
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id, models.Vendor.tenant_id == tenant_id).first()

def get_vendors(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.Vendor).filter(models.Vendor.tenant_id == tenant_id).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate, tenant_id: str = "default_tenant"):
    db_vendor = models.Vendor(**vendor.model_dump(), tenant_id=tenant_id)
    if db_vendor.risk_score is None:
        db_vendor.risk_score = 50.0
    if db_vendor.risk_score >= 80:
        db_vendor.risk_level = models.RiskLevel.CRITICAL
    elif db_vendor.risk_score >= 60:
        db_vendor.risk_level = models.RiskLevel.HIGH
    elif db_vendor.risk_score >= 30:
        db_vendor.risk_level = models.RiskLevel.MEDIUM
    else:
        db_vendor.risk_level = models.RiskLevel.LOW
        
    db_vendor.last_assessment_date = datetime.utcnow()
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# Phishing Incident CRUD
def create_phishing_incident(db: Session, incident: schemas.PhishingIncidentCreate, tenant_id: str = "default_tenant"):
    db_incident = models.PhishingIncident(**incident.model_dump(), tenant_id=tenant_id)
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def get_phishing_incidents(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.PhishingIncident).filter(models.PhishingIncident.tenant_id == tenant_id).order_by(models.PhishingIncident.analyzed_at.desc()).offset(skip).limit(limit).all()

# Compliance Query CRUD
def create_compliance_query(db: Session, query: schemas.ComplianceQueryCreate, tenant_id: str = "default_tenant"):
    db_query = models.ComplianceQuery(**query.model_dump(), tenant_id=tenant_id)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def get_compliance_queries(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.ComplianceQuery).filter(models.ComplianceQuery.tenant_id == tenant_id).order_by(models.ComplianceQuery.query_at.desc()).offset(skip).limit(limit).all()

# Audit Readiness CRUD
def create_audit_readiness(db: Session, audit: schemas.AuditReadinessCreate, tenant_id: str = "default_tenant"):
    db_audit = models.AuditReadiness(**audit.model_dump(), tenant_id=tenant_id)
    db_audit.assessed_at = datetime.utcnow()
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

def get_audit_readiness(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.AuditReadiness).filter(models.AuditReadiness.tenant_id == tenant_id).order_by(models.AuditReadiness.assessed_at.desc()).offset(skip).limit(limit).all()

# Training Completion CRUD
def create_training_completion(db: Session, completion: schemas.TrainingCompletionCreate, tenant_id: str = "default_tenant"):
    db_completion = models.TrainingCompletion(**completion.model_dump(), tenant_id=tenant_id)
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion

def get_training_completions(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.TrainingCompletion).filter(models.TrainingCompletion.tenant_id == tenant_id).order_by(models.TrainingCompletion.completed_at.desc()).offset(skip).limit(limit).all()

# Audit Log CRUD
def create_audit_log(db: Session, log: schemas.AuditLogCreate, tenant_id: str = "default_tenant"):
    db_log = models.AuditLog(**log.model_dump(), tenant_id=tenant_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs(db: Session, tenant_id: str = "default_tenant", skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).filter(models.AuditLog.tenant_id == tenant_id).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
