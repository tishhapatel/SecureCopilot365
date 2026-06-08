from sqlalchemy.orm import Session
from db import models, schemas
from datetime import datetime

# Employee CRUD
def get_employee(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_entra_id(db: Session, entra_id: str):
    return db.query(models.Employee).filter(models.Employee.entra_id == entra_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee_scores(db: Session, employee_id: str, risk_score: float, awareness_score: float):
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db_employee.risk_score = risk_score
        db_employee.awareness_score = awareness_score
        db.commit()
        db.refresh(db_employee)
    return db_employee

# Vendor CRUD
def get_vendor(db: Session, vendor_id: str):
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def get_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate):
    db_vendor = models.Vendor(**vendor.model_dump())
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
def create_phishing_incident(db: Session, incident: schemas.PhishingIncidentCreate):
    db_incident = models.PhishingIncident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def get_phishing_incidents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PhishingIncident).order_by(models.PhishingIncident.analyzed_at.desc()).offset(skip).limit(limit).all()

# Compliance Query CRUD
def create_compliance_query(db: Session, query: schemas.ComplianceQueryCreate):
    db_query = models.ComplianceQuery(**query.model_dump())
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def get_compliance_queries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ComplianceQuery).order_by(models.ComplianceQuery.query_at.desc()).offset(skip).limit(limit).all()

# Audit Readiness CRUD
def create_audit_readiness(db: Session, audit: schemas.AuditReadinessCreate):
    db_audit = models.AuditReadiness(**audit.model_dump())
    db_audit.assessed_at = datetime.utcnow()
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

def get_audit_readiness(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditReadiness).order_by(models.AuditReadiness.assessed_at.desc()).offset(skip).limit(limit).all()

# Training Completion CRUD
def create_training_completion(db: Session, completion: schemas.TrainingCompletionCreate):
    db_completion = models.TrainingCompletion(**completion.model_dump())
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion

def get_training_completions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TrainingCompletion).order_by(models.TrainingCompletion.completed_at.desc()).offset(skip).limit(limit).all()

# Audit Log CRUD
def create_audit_log(db: Session, log: schemas.AuditLogCreate):
    db_log = models.AuditLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
