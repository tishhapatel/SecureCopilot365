# SecureCopilot 365 🛡️🤖

**SecureCopilot 365** is a production-grade, enterprise-ready AI Cybersecurity, Compliance, and Risk Management Agent designed for Microsoft 365 Copilot. It integrates seamlessly with Microsoft Teams, Outlook, Word, and SharePoint to deliver real-time security insights, automated compliance gap audits, vendor risk analysis, and interactive security coaching.

---

## 🌟 Key Features

*   **🛡️ Multi-Agent Orchestrator**: Uses a master routing agent that parses user intent and delegates tasks to domain-specific security agents.
*   **✉️ Real-Time Phishing & BEC Detection**: Scans emails for domain spoofing, lookalike domains, Business Email Compromise (BEC) patterns, and urgency/coercion language.
*   **📋 Regulatory Compliance Analyzer**: Instantly audits policies and documents against frameworks like **ISO 27001**, **GDPR**, and **NIST CSF 2.0**.
*   **🏢 Third-Party Risk Management (TPRM)**: Automates vendor risk assessment based on questionnaires and security certifications, plotting risks on a visual heatmap.
*   **✅ Audit Readiness Evidence Collector**: Gathers Tenant configurations and evidence logs to assess compliance status.
*   **🎓 Interactive Security Coach**: Delivers personalized, role-specific security awareness training scenarios directly to employees.
*   **🧠 Advanced IQ Layer**: Powered by **Work IQ** (organizational context), **Foundry IQ** (vector-based RAG pipelines), and **Fabric IQ** (semantic mapping of threats to controls).

---

## 🏗️ Architecture Overview

SecureCopilot 365 is divided into three key services under the `apps/` directory:

```mermaid
graph TD
    User([User / CISO]) -->|React Web App| FE[Frontend Dashboard]
    Teams[MS Teams / Outlook] -->|Chat & Cards| Bot[Teams Bot]
    FE -->|REST API| BE[FastAPI Backend]
    Bot -->|REST API| BE
    
    subgraph Backend [FastAPI Backend Service]
        BE --> ORCH[Orchestrator Agent]
        ORCH --> AG_P[Phishing Agent]
        ORCH --> AG_C[Compliance Agent]
        ORCH --> AG_V[Vendor Agent]
        ORCH --> AG_A[Audit Agent]
        ORCH --> AG_W[Awareness Coach]
        
        BE --> IQ[IQ Layers: Work / Foundry / Fabric]
        IQ --> DB[(SQL Database)]
        IQ --> Search[(Azure AI Search / RAG)]
        BE --> Graph[Microsoft Graph Client]
    end
```

1.  **FastAPI Backend (`apps/backend`)**: Core business logic, orchestration engine, domain agents, and database operations.
2.  **React Frontend Dashboard (`apps/frontend`)**: A modern CISO-focused UI with real-time risk telemetry, compliance heatmaps, security logs, and a Chatbot interface.
3.  **Teams Bot (`apps/teams-bot`)**: An interactive bot constructed using the Teams AI library to intercept reported threats, evaluate them with backend agents, and display findings via Adaptive Cards.

---

## ⚙️ Configuration & Environment Setup

### 1. Backend Config
Rename [apps/backend/.env.example](file:///d:/SecureCopilot365/apps/backend/.env.example) to `.env` inside `apps/backend/` and configure:
*   **Azure OpenAI**: Credentials for agent reasoning and embeddings.
*   **Microsoft Entra ID**: Application registrations for authentication.
*   **Microsoft Graph API**: Scopes and base URLs for fetching tenant data.
*   **Database**: SQLite for local testing or Azure SQL Connection String.
*   **Azure AI Search**: Vector database details for the RAG compliance modules.

---

## 🚀 Getting Started

Ensure you have **Python 3.10+** and **Node.js 18+** installed.

### Quick Start (Simultaneous Run)
Run the project orchestration script from the root directory:
```bash
python run_project.py
```
This automatically boots all three core services simultaneously:
*   **FastAPI Backend**: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`)
*   **React Frontend Dashboard**: `http://localhost:5173`
*   **Teams Bot**: `http://localhost:3978`

---

### Manual Startup & Setup

#### 1. Setup the Backend
Navigate to the backend directory, create a virtual environment, install requirements, and run the service:
```bash
cd apps/backend
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Seed & Ingest the Knowledge Base (RAG)
To populate the compliance frameworks (ISO 27001, GDPR, NIST CSF) in your vector storage or local mock database:
```bash
python knowledge-base/ingest.py
```

#### 3. Start the React Frontend Dashboard
Navigate to the frontend directory, install dependencies, and start the development server:
```bash
cd apps/frontend
npm install
npm run dev
```

#### 4. Run the Microsoft Teams Bot
Navigate to the bot directory, install dependencies, and start the service:
```bash
cd apps/teams-bot
npm install
npm start
```

---

## 🧪 Verification & Testing
To run the automated test suite verifying agent behavior, model endpoints, and input sanitization:
```bash
cd apps/backend
pytest ../../tests/
```

To run a production compilation audit on the React frontend:
```bash
cd apps/frontend
npm run build
```

---

## 📦 Cloud Deployment
The infrastructure is fully defined as Bicep templates within the `/infra` folder. To deploy the backend, frontend container app, database, and Cognitive Services on Azure, configure [infra/main.parameters.json](file:///d:/SecureCopilot365/infra/main.parameters.json) and execute:
```bash
az deployment sub create --location <location> --template-file infra/main.bicep --parameters infra/main.parameters.json
```
