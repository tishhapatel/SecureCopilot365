"""
Database models for SecureCopilot 365.
Schema: Employee → Department → Asset → Threat → Risk → Control → Compliance
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum, uuid

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class RiskLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    entra_id = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(255))
    job_title = Column(String(255))
    manager_id = Column(String(36), ForeignKey("employees.id"))
    risk_score = Column(Float, default=0.0)
    awareness_score = Column(Float, default=0.0)
    last_training_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    # Relationships
    phishing_incidents = relationship("PhishingIncident", back_populates="employee")
    compliance_queries = relationship("ComplianceQuery", back_populates="employee")
    training_completions = relationship("TrainingCompletion", back_populates="employee")

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    website = Column(String(500))
    data_categories = Column(Text)          # JSON: list of data categories processed
    risk_score = Column(Float, default=50.0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    iso27001_certified = Column(Boolean, default=False)
    soc2_type2 = Column(Boolean, default=False)
    gdpr_dpa_signed = Column(Boolean, default=False)
    last_assessment_date = Column(DateTime)
    sub_processors = Column(Text)           # JSON: list of sub-processors
    questionnaire_score = Column(Float)
    pen_test_date = Column(DateTime)
    incident_history = Column(Text)         # JSON: list of known incidents
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class PhishingIncident(Base):
    __tablename__ = "phishing_incidents"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    email_subject = Column(String(500))
    sender_domain = Column(String(255))
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    mitre_techniques = Column(Text)         # JSON: list of detected ATT&CK IDs
    indicators = Column(Text)              # JSON: list of detection reasons
    user_action = Column(String(50))       # reported | clicked | ignored
    reported_to_soc = Column(Boolean, default=False)
    analyzed_at = Column(DateTime, server_default=func.now())
    employee = relationship("Employee", back_populates="phishing_incidents")

class ComplianceQuery(Base):
    __tablename__ = "compliance_queries"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    employee_id = Column(String(36), ForeignKey("employees.id"))
    document_name = Column(String(500))
    frameworks_checked = Column(Text)      # JSON: ["ISO27001", "GDPR", "NIST"]
    gaps_found = Column(Integer, default=0)
    gap_details = Column(Text)             # JSON: list of gap objects
    remediation_provided = Column(Boolean, default=True)
    citations = Column(Text)              # JSON: list of framework citations
    query_at = Column(DateTime, server_default=func.now())
    employee = relationship("Employee", back_populates="compliance_queries")

class AuditReadiness(Base):
    __tablename__ = "audit_readiness"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    framework = Column(String(100), nullable=False)   # ISO27001, SOC2, NIST, etc.
    overall_score = Column(Float, nullable=False)
    controls_total = Column(Integer)
    controls_evidenced = Column(Integer)
    controls_partial = Column(Integer)
    controls_missing = Column(Integer)
    critical_gaps = Column(Text)          # JSON: list of critical gap objects
    evidence_package = Column(Text)       # JSON: collected evidence references
    assessed_at = Column(DateTime, server_default=func.now())
    assessed_by = Column(String(36), ForeignKey("employees.id"))

class TrainingCompletion(Base):
    __tablename__ = "training_completions"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    score = Column(Float)
    passed = Column(Boolean)
    certificate_id = Column(String(36), default=gen_uuid)
    completed_at = Column(DateTime, server_default=func.now())
    employee = relationship("Employee", back_populates="training_completions")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_entra_id = Column(String(255), index=True)
    action = Column(String(100), nullable=False)
    agent = Column(String(100))
    query_hash = Column(String(64))        # SHA-256 of query, not raw query
    response_category = Column(String(100))
    risk_level = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, server_default=func.now(), index=True)
