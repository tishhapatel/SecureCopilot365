"""
Permissions and role-to-permission mapping for SecureCopilot 365
"""
from auth import roles

# Permission Constants
MANAGE_TENANTS = "MANAGE_TENANTS"
MANAGE_USERS = "MANAGE_USERS"
VIEW_INCIDENTS = "VIEW_INCIDENTS"
SUBMIT_REPORTS = "SUBMIT_REPORTS"
VIEW_COMPLIANCE = "VIEW_COMPLIANCE"
RUN_COMPLIANCE = "RUN_COMPLIANCE"
VIEW_VENDORS = "VIEW_VENDORS"
MANAGE_VENDORS = "MANAGE_VENDORS"
VIEW_AUDITS = "VIEW_AUDITS"
RUN_AUDITS = "RUN_AUDITS"
VIEW_AWARENESS = "VIEW_AWARENESS"
ASSIGN_AWARENESS = "ASSIGN_AWARENESS"
RUN_AWARENESS = "RUN_AWARENESS"

ALL_PERMISSIONS = [
    {"name": MANAGE_TENANTS, "module": "admin"},
    {"name": MANAGE_USERS, "module": "admin"},
    {"name": VIEW_INCIDENTS, "module": "phishing"},
    {"name": SUBMIT_REPORTS, "module": "phishing"},
    {"name": VIEW_COMPLIANCE, "module": "compliance"},
    {"name": RUN_COMPLIANCE, "module": "compliance"},
    {"name": VIEW_VENDORS, "module": "vendor"},
    {"name": MANAGE_VENDORS, "module": "vendor"},
    {"name": VIEW_AUDITS, "module": "audit"},
    {"name": RUN_AUDITS, "module": "audit"},
    {"name": VIEW_AWARENESS, "module": "awareness"},
    {"name": ASSIGN_AWARENESS, "module": "awareness"},
    {"name": RUN_AWARENESS, "module": "awareness"},
]

# Role to Permission mapping
ROLE_PERMISSIONS = {
    roles.SUPER_ADMIN: [
        MANAGE_TENANTS, MANAGE_USERS, VIEW_INCIDENTS, SUBMIT_REPORTS,
        VIEW_COMPLIANCE, RUN_COMPLIANCE, VIEW_VENDORS, MANAGE_VENDORS,
        VIEW_AUDITS, RUN_AUDITS, VIEW_AWARENESS, ASSIGN_AWARENESS, RUN_AWARENESS
    ],
    roles.CISO: [
        MANAGE_USERS, VIEW_INCIDENTS, SUBMIT_REPORTS,
        VIEW_COMPLIANCE, RUN_COMPLIANCE, VIEW_VENDORS, MANAGE_VENDORS,
        VIEW_AUDITS, RUN_AUDITS, VIEW_AWARENESS, ASSIGN_AWARENESS, RUN_AWARENESS
    ],
    roles.AUDITOR: [
        VIEW_INCIDENTS, VIEW_COMPLIANCE, VIEW_VENDORS, VIEW_AUDITS, RUN_AWARENESS
    ],
    roles.HR: [
        VIEW_AWARENESS, ASSIGN_AWARENESS, RUN_AWARENESS
    ],
    roles.COMPLIANCE: [
        VIEW_COMPLIANCE, RUN_COMPLIANCE, VIEW_AUDITS, RUN_AUDITS, RUN_AWARENESS
    ],
    roles.VENDOR_MANAGER: [
        VIEW_VENDORS, MANAGE_VENDORS, RUN_AWARENESS
    ],
    roles.EMPLOYEE: [
        SUBMIT_REPORTS, RUN_AWARENESS
    ]
}
