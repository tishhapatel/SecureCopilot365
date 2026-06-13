from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from db.models import RiskLevel

# Employee Schemas
class EmployeeBase(BaseModel):
    entra_id: str
    display_name: str
    email: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    manager_id: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: str
    risk_score: float
    awareness_score: float
    last_training_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Vendor Schemas
class VendorBase(BaseModel):
    name: str
    website: Optional[str] = None
    data_categories: Optional[str] = None # JSON string
    iso27001_certified: Optional[bool] = False
    soc2_type2: Optional[bool] = False
    gdpr_dpa_signed: Optional[bool] = False
    sub_processors: Optional[str] = None # JSON string
    questionnaire_score: Optional[float] = None
    pen_test_date: Optional[datetime] = None
    incident_history: Optional[str] = None # JSON string
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: str
    risk_score: float
    risk_level: RiskLevel
    last_assessment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Phishing Incident Schemas
class PhishingIncidentBase(BaseModel):
    employee_id: str
    email_subject: Optional[str] = None
    sender_domain: Optional[str] = None
    risk_score: float
    risk_level: RiskLevel
    mitre_techniques: Optional[str] = None # JSON string
    indicators: Optional[str] = None # JSON string
    user_action: Optional[str] = None # reported | clicked | ignored
    reported_to_soc: Optional[bool] = False

class PhishingIncidentCreate(PhishingIncidentBase):
    pass

class PhishingIncident(PhishingIncidentBase):
    id: str
    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Compliance Query Schemas
class ComplianceQueryBase(BaseModel):
    employee_id: Optional[str] = None
    document_name: Optional[str] = None
    frameworks_checked: Optional[str] = None # JSON string
    gaps_found: Optional[int] = 0
    gap_details: Optional[str] = None # JSON string
    remediation_provided: Optional[bool] = True
    citations: Optional[str] = None # JSON string

class ComplianceQueryCreate(ComplianceQueryBase):
    pass

class ComplianceQuery(ComplianceQueryBase):
    id: str
    query_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Audit Readiness Schemas
class AuditReadinessBase(BaseModel):
    framework: str
    overall_score: float
    controls_total: Optional[int] = 0
    controls_evidenced: Optional[int] = 0
    controls_partial: Optional[int] = 0
    controls_missing: Optional[int] = 0
    critical_gaps: Optional[str] = None # JSON string
    evidence_package: Optional[str] = None # JSON string
    assessed_by: Optional[str] = None

class AuditReadinessCreate(AuditReadinessBase):
    pass

class AuditReadiness(AuditReadinessBase):
    id: str
    assessed_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Training Completion Schemas
class TrainingCompletionBase(BaseModel):
    employee_id: str
    topic: str
    score: Optional[float] = None
    passed: Optional[bool] = None

class TrainingCompletionCreate(TrainingCompletionBase):
    pass

class TrainingCompletion(TrainingCompletionBase):
    id: str
    certificate_id: str
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogBase(BaseModel):
    user_entra_id: Optional[str] = None
    user_id: Optional[str] = None
    action: str
    agent: Optional[str] = None
    query_hash: Optional[str] = None
    response_category: Optional[str] = None
    risk_level: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tenant_id: Optional[str] = "default_tenant"

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Permission Schemas
class PermissionResponse(BaseModel):
    id: str
    permission_name: str
    module: str
    model_config = ConfigDict(from_attributes=True)

# Role Schemas
class RoleResponse(BaseModel):
    id: str
    role_name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    department: Optional[str] = None
    tenant_id: Optional[str] = "default_tenant"

class UserCreate(UserBase):
    password: str
    role_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: RoleResponse
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

