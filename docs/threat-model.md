# Threat Modeling — SecureCopilot 365

This document details the security threat model, vulnerability classifications, and mitigation strategies implemented in SecureCopilot 365.

---

## 1. STRIDE Assessment

| Threat Category | Target Component | Threat Vector Scenario | Platform Mitigation |
| :--- | :--- | :--- | :--- |
| **Spoofing** | API Endpoints / Auth | An attacker attempts to forge authentication tokens or spoof a tenant administrator profile. | Entra ID OIDC SSO validation and cryptographically signed JWT tokens with short (1h) expiration windows. |
| **Tampering** | Audit Logs Database | An administrator attempts to modify security history to hide unauthorized actions. | SHA-256 hash-chained audit log ledger. Tampering breaks the validation chain. |
| **Repudiation** | Audit Verification | A user claims they did not run a specific API request or database query. | IP addresses, user agents, and query hashes are logged in the cryptographically chained ledger. |
| **Information Disclosure** | Database Queries | An authenticated tenant user queries records belonging to a different tenant. | Logical tenant boundaries enforced by SQLAlchemy query filters in development and database-level RLS in production. |
| **Denial of Service** | API Gateway | An attacker floods backend endpoints with requests to exhaust API resources. | In-memory sliding window rate-limiting middleware (Max 100 req/min). |
| **Elevation of Privilege** | RBAC Policies | A general employee attempts to access CISO dashboard reports. | Gated dependencies in [deps.py](file:///d:/SecureCopilot365/apps/backend/api/deps.py) verify roles against specific permissions (e.g. `VIEW_AUDITS`). |

---

## 2. OWASP API Top 10 Mappings

*   **API1:2023 Broken Object Level Authorization (BOLA)**: Gated query generation filters all SQL transactions using the active session's `tenant_id` context.
*   **API2:2023 Broken Authentication**: Gated API routes verify authorization headers and JWT session parameters.
*   **API4:2023 Unrestricted Resource Consumption**: The rate-limiting middleware blocks access attempts that exceed request limits.
*   **API5:2023 Broken Function Level Authorization (BFLA)**: Permissions are verified before routing requests to administration endpoints.

---

## 3. MITRE ATT&CK Mitigation Matrix

SecureCopilot 365 maps detected threat indicators directly to ATT&CK mitigations:
*   **T1566.002 (Spearphishing Link)**: Analyzed by the Phishing Agent. Mitigated by checking sender reputation, domain indicators, and URL security.
*   **T1598 (Social Engineering)**: Addressed by the Awareness Coach training modules, raising awareness of BEC wire transfer requests.
*   **T1078 (Valid Accounts)**: Managed by continuous Zero Trust checks, verification of device compliance, and impossible travel detection.
