# Implementation Plan — SecureCopilot 365

SecureCopilot 365 is a production-grade, enterprise-ready AI Cybersecurity, Compliance, and Risk Management Agent designed for Microsoft 365 Copilot. It integrates with Microsoft Teams, Outlook, Word, and SharePoint, providing real-time phishing detection, compliance checks (ISO 27001, NIST CSF, GDPR, etc.), vendor risk scoring, audit readiness, and personalized security training.

Due to the length of the hackathon specification, the input prompt was truncated. This plan maps out the repository structure, details the components we have, and outlines how we can proceed with the rest of the application.

---

## User Review Required

> [!WARNING]
> **Truncated Prompt Ingestion**
> The build specification was truncated in your prompt. Specifically, we have details for:
> - **Section 1**: Repository structure and `.env.example`
> - **Section 2**: FastAPI main application (`main.py`) and SQLAlchemy DB Models (`models.py`)
> - **Section 3**: AI Agents up to the beginning of the `awareness_agent.py` (Security Awareness Coach).
>
> We are missing:
> - The end of the Security Awareness Coach Agent.
> - The details of the IQ layers (`work_iq.py`, `foundry_iq.py`, `fabric_iq.py`).
> - The Microsoft Graph API client (`graph/` modules).
> - API routers/endpoints (`api/routes/*`), middlewares, and dependency injection (`deps.py`).
> - The entire frontend React + Vite dashboard and components.
> - The Teams Bot application code and manifest.
> - Ingestion scripts, knowledge source JSON files, infrastructure files, and test files.

---

## Open Questions

> [!IMPORTANT]
> Please review and provide feedback on the following questions before we begin:
> 
> 1. **Can you provide the missing parts of the specification?** If you have the original untruncated prompt (e.g., Sections 4, 5, etc.), please paste the remaining sections in your next message.
> 2. **Alternative — Custom Architecture:** If you do not have the rest of the prompt, would you like me to design and implement the remaining components (React dashboard, Teams bot, RAG layers, Graph client, routers, etc.) from scratch using premium design systems and industry-standard practices?
> 3. **Tailwind CSS version:** For the frontend, the directory structure specifies `tailwind.config.ts`. If we proceed with building the frontend, what version of Tailwind CSS should we use (e.g., Tailwind v3 or v4)?
> 4. **Azure Services & DB Configuration:** Do you have active endpoints/keys for Azure OpenAI and Azure SQL/Search, or should we set up local mocks (e.g., SQLite, local semantic search, OpenAI API mocks) to ensure the code runs and tests successfully out-of-the-box in development?

---

## Proposed Changes

Here is the proposed layout of files to be created or modified, grouped by component:

### 1. Repository Setup & Dependencies
Initial configuration files for backend, frontend, and Teams bot.

*   #### [NEW] [.gitignore](file:///d:/SecureCopilot365/.gitignore)
    Configure Git to ignore `node_modules`, `.env`, `venv`, `__pycache__`, and DB logs.
*   #### [NEW] [docker-compose.yml](file:///d:/SecureCopilot365/docker-compose.yml)
    Services for local deployment: FastAPI backend, React frontend, and local PostgreSQL/MSSQL container.
*   #### [NEW] [apps/backend/requirements.txt](file:///d:/SecureCopilot365/apps/backend/requirements.txt)
    FastAPI, SQLAlchemy, Pydantic, Azure OpenAI, Microsoft Graph API client libraries, pyodbc/psycopg2, and testing libs.
*   #### [NEW] [apps/backend/Dockerfile](file:///d:/SecureCopilot365/apps/backend/Dockerfile)
    Docker configuration for the FastAPI service.
*   #### [NEW] [apps/backend/.env.example](file:///d:/SecureCopilot365/apps/backend/.env.example)
    As specified in Section 1.2.

---

### 2. Backend Application Core & Database
Setting up the FastAPI app instance, middleware, and database schemas.

*   #### [NEW] [apps/backend/main.py](file:///d:/SecureCopilot365/apps/backend/main.py)
    FastAPI startup, lifespan context, CORS setup, middleware registration, and router imports (as defined in Section 2.1).
*   #### [NEW] [apps/backend/db/models.py](file:///d:/SecureCopilot365/apps/backend/db/models.py)
    SQLAlchemy models representing the schema (Employee, Vendor, PhishingIncident, ComplianceQuery, AuditReadiness, TrainingCompletion, AuditLog).
*   #### [NEW] [apps/backend/db/database.py](file:///d:/SecureCopilot365/apps/backend/db/database.py)
    DB connection setup, engine initialization, session generator, and table creation helper.
*   #### [NEW] [apps/backend/db/schemas.py](file:///d:/SecureCopilot365/apps/backend/db/schemas.py)
    Pydantic schemas for request validation and response serialization for all models.
*   #### [NEW] [apps/backend/db/crud.py](file:///d:/SecureCopilot365/apps/backend/db/crud.py)
    Common CRUD operations for database models.

---

### 3. Middleware & Security Layers
Protecting the backend API against prompt injection, role violations, and securing authentication.

*   #### [NEW] [apps/backend/api/middleware/auth.py](file:///d:/SecureCopilot365/apps/backend/api/middleware/auth.py)
    Microsoft Entra ID JWT validation middleware.
*   #### [NEW] [apps/backend/api/middleware/rbac.py](file:///d:/SecureCopilot365/apps/backend/api/middleware/rbac.py)
    Role-based access controls for endpoints (e.g., CISO vs. regular employee).
*   #### [NEW] [apps/backend/api/middleware/audit_log.py](file:///d:/SecureCopilot365/apps/backend/api/middleware/audit_log.py)
    Immutable audit logging middleware logging hashing queries and actions.
*   #### [NEW] [apps/backend/api/middleware/sanitize.py](file:///d:/SecureCopilot365/apps/backend/api/middleware/sanitize.py)
    Prompt injection sanitization filter.
*   #### [NEW] [apps/backend/api/deps.py](file:///d:/SecureCopilot365/apps/backend/api/deps.py)
    Dependency injection providers (DB session, current user, authenticated Graph client).

---

### 4. AI Agents Implementation
Developing the orchestration agent and domain-specific agents.

*   #### [NEW] [apps/backend/agents/base_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/base_agent.py)
    Shared base class wrapping OpenAI interactions, input sanitization, and basic RAG hooks.
*   #### [NEW] [apps/backend/agents/orchestrator.py](file:///d:/SecureCopilot365/apps/backend/agents/orchestrator.py)
    Master routing agent that interprets user requests and delegates to specific agents.
*   #### [NEW] [apps/backend/agents/phishing_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/phishing_agent.py)
    Domain spoofing, lookalike domain, BEC, and urgency NLP analyzer.
*   #### [NEW] [apps/backend/agents/compliance_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/compliance_agent.py)
    ISO 27001, GDPR, NIST compliance document gap analyzer.
*   #### [NEW] [apps/backend/agents/vendor_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/vendor_agent.py)
    Third-party risk management scoring based on questionnaires and certificates.
*   #### [NEW] [apps/backend/agents/audit_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/audit_agent.py)
    Audit readiness assessment based on evidence gathered from Microsoft 365.
*   #### [NEW] [apps/backend/agents/awareness_agent.py](file:///d:/SecureCopilot365/apps/backend/agents/awareness_agent.py)
    Security Awareness Coach. We will complete the truncated implementation with interactive role-specific training scenarios.

---

### 5. IQ Layer (Work, Foundry, and Fabric IQ)
The context, RAG, and semantic reasoning layer for the agents.

*   #### [NEW] [apps/backend/iq/work_iq.py](file:///d:/SecureCopilot365/apps/backend/iq/work_iq.py)
    Resolves organizational context, user details, and job-based permission scopes.
*   #### [NEW] [apps/backend/iq/foundry_iq.py](file:///d:/SecureCopilot365/apps/backend/iq/foundry_iq.py)
    Vector search pipeline mapping search queries to compliance frameworks and threat intelligence.
*   #### [NEW] [apps/backend/iq/fabric_iq.py](file:///d:/SecureCopilot365/apps/backend/iq/fabric_iq.py)
    Semantic ontology mapping threats to compliance controls.

---

### 6. Microsoft Graph API Integration
Retrieving actual organization context for grounding security recommendations.

*   #### [NEW] [apps/backend/graph/client.py](file:///d:/SecureCopilot365/apps/backend/graph/client.py)
    Core client initialization with Entra ID credential delegation.
*   #### [NEW] [apps/backend/graph/users.py](file:///d:/SecureCopilot365/apps/backend/graph/users.py)
    Retrieves user profile, direct reports, and department info.
*   #### [NEW] [apps/backend/graph/mail.py](file:///d:/SecureCopilot365/apps/backend/graph/mail.py)
    Accesses and processes email messages for phishing analysis.
*   #### [NEW] [apps/backend/graph/sharepoint.py](file:///d:/SecureCopilot365/apps/backend/graph/sharepoint.py)
    Retrieves documents and policies from SharePoint libraries for compliance audits.

---

### 7. API Routers & Endpoints
Exposing backend functionality via REST endpoints.

*   #### [NEW] [apps/backend/api/routes/agents.py](file:///d:/SecureCopilot365/apps/backend/api/routes/agents.py)
    Endpoint for orchestrator routing.
*   #### [NEW] [apps/backend/api/routes/phishing.py](file:///d:/SecureCopilot365/apps/backend/api/routes/phishing.py)
    Email analysis endpoint.
*   #### [NEW] [apps/backend/api/routes/compliance.py](file:///d:/SecureCopilot365/apps/backend/api/routes/compliance.py)
    Document checking endpoint.
*   #### [NEW] [apps/backend/api/routes/vendor.py](file:///d:/SecureCopilot365/apps/backend/api/routes/vendor.py)
    Vendor risk assessment endpoints.
*   #### [NEW] [apps/backend/api/routes/audit.py](file:///d:/SecureCopilot365/apps/backend/api/routes/audit.py)
    Audit readiness status and evidence bundle endpoints.
*   #### [NEW] [apps/backend/api/routes/awareness.py](file:///d:/SecureCopilot365/apps/backend/api/routes/awareness.py)
    Interactive security awareness coach endpoints.
*   #### [NEW] [apps/backend/api/routes/dashboard.py](file:///d:/SecureCopilot365/apps/backend/api/routes/dashboard.py)
    CISO dashboard summary endpoints.

---

### 8. Frontend React Application
The premium frontend dashboard (using React, Vite, and Tailwind CSS / Vanilla CSS).

*   #### [NEW] [apps/frontend/package.json](file:///d:/SecureCopilot365/apps/frontend/package.json)
    React, React Router, Vite, Tailwind CSS, Lucide React, and Recharts.
*   #### [NEW] [apps/frontend/tailwind.config.ts](file:///d:/SecureCopilot365/apps/frontend/tailwind.config.ts)
    Theme extension definitions for dark mode and dynamic glows.
*   #### [NEW] [apps/frontend/src/App.tsx](file:///d:/SecureCopilot365/apps/frontend/src/App.tsx)
    Main entry point with layout grid, sidebar navigation, and routing.
*   #### [NEW] [apps/frontend/src/components/dashboard/CISODashboard.tsx](file:///d:/SecureCopilot365/apps/frontend/src/components/dashboard/CISODashboard.tsx)
    High-fidelity main CISO summary layout.
*   #### [NEW] [apps/frontend/src/components/dashboard/RiskScoreGauge.tsx](file:///d:/SecureCopilot365/apps/frontend/src/components/dashboard/RiskScoreGauge.tsx)
    Visual dial displaying overall tenant risk score.
*   #### [NEW] [apps/frontend/src/components/dashboard/VendorHeatmap.tsx](file:///d:/SecureCopilot365/apps/frontend/src/components/dashboard/VendorHeatmap.tsx)
    Visual TPRM matrix of third-party risk.
*   #### [NEW] [apps/frontend/src/components/chat/ChatInterface.tsx](file:///d:/SecureCopilot365/apps/frontend/src/components/chat/ChatInterface.tsx)
    Sidebar Copilot chat component supporting RAG citations.
*   *(Other pages and components listed in structure will be created with premium aesthetics: custom gradients, clean typography, hover feedback, and reactive interfaces)*

---

### 9. Microsoft Teams Bot
The bot interaction interface for Microsoft M365 environment.

*   #### [NEW] [apps/teams-bot/package.json](file:///d:/SecureCopilot365/apps/teams-bot/package.json)
    Teams AI library, Bot Framework SDK dependencies.
*   #### [NEW] [apps/teams-bot/bot.js](file:///d:/SecureCopilot365/apps/teams-bot/bot.js)
    Handles incoming chat activities, invokes agents, and generates Adaptive Cards.
*   #### [NEW] [apps/teams-bot/cards/phishing_card.json](file:///d:/SecureCopilot365/apps/teams-bot/cards/phishing_card.json)
    Adaptive Card showing the threat severity breakdown and reported/safe options.

---

### 10. Knowledge Ingestion & Docs
Files to seed the RAG vector search index and system documentation.

*   #### [NEW] [knowledge-base/ingest.py](file:///d:/SecureCopilot365/knowledge-base/ingest.py)
    Reads source JSON files and ingests them into vector storage or local JSON-based mock index for development.
*   #### [NEW] [knowledge-base/sources/gdpr_articles.json](file:///d:/SecureCopilot365/knowledge-base/sources/gdpr_articles.json)
    Structured list of GDPR articles 5, 6, 13, 17, 25, 32, 33, 35.
*   #### [NEW] [knowledge-base/sources/iso27001_controls.json](file:///d:/SecureCopilot365/knowledge-base/sources/iso27001_controls.json)
    Full 93 controls from ISO 27001:2022.
*   #### [NEW] [knowledge-base/sources/nist_csf2_functions.json](file:///d:/SecureCopilot365/knowledge-base/sources/nist_csf2_functions.json)
    NIST CSF 2.0 framework layout.

---

## Verification Plan

### Automated Verification
1.  **Backend Pytests:**
    Validate agents return standard JSON formats and handle prompt injections.
    ```bash
    pytest tests/
    ```
2.  **Frontend Compilation:**
    Ensure TypeScript compilation and build processes complete error-free.
    ```bash
    cd apps/frontend && npm run build
    ```

### Manual Verification
1.  **FastAPI Interactive OpenAPI UI:**
    Run backend server locally, navigate to `http://localhost:8000/docs`, and execute API endpoints (Phishing scan, Compliance check) using mocked test inputs.
2.  **Frontend UX Validation:**
    Boot the dev server, visit the CISO dashboard, click through subpages (Phishing, Vendor, Audit), and interact with the Copilot chatbot to verify markdown rendering and citation links.
