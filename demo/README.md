# SecureCopilot 365 — Interactive Demo

Welcome to the SecureCopilot 365 interactive demonstration.

## 🎬 Demo Video Overview

This folder contains a full cinematic product demonstration video (`SecureCopilot365_Demo.webm`). The video showcases the core functionality of the AI agents and the Zero Trust architecture in action.

### How to watch
The `SecureCopilot365_Demo.webm` file can be opened directly in any modern web browser (Edge, Chrome, Firefox) or standard video player (like VLC). 

---

## 📸 Application Page Walkthrough

Below are screenshots captured directly from the live application, demonstrating the key pages and features powered by the Multi-Agent LLM architecture.

### 1. CISO Command Center Dashboard
![CISO Dashboard](screenshots/01_CISO_Dashboard.png)
**What it does:** The global command center aggregates data across all underlying security agents. It displays real-time telemetry including a live Threat Feed, the active Tenant Risk Index, Department Risk Breakdown, and the overall Framework Coverage radar chart. It acts as the "single pane of glass" for the CISO to monitor Microsoft 365 tenant security.

### 2. Phishing Threat Intelligence
![Phishing Detection](screenshots/02_Phishing_Detection.png)
**What it does:** This page demonstrates the **Phishing Agent**. The agent performs deep email header analysis (SPF/DKIM/DMARC), semantic content analysis to detect urgency and Business Email Compromise (BEC) patterns, and maps identified threats directly to MITRE ATT&CK techniques (e.g., T1566.002 Spearphishing Link).

### 3. Compliance Intelligence Hub
![Compliance Advisor](screenshots/03_Compliance_Advisor.png)
**What it does:** Powered by the **Compliance Agent**, this page automatically ingests organizational documents (such as an Information Security Policy) and cross-references them against major frameworks like GDPR, ISO 27001, and NIST CSF. It highlights specific control gaps (e.g., ISO A.8.24) and provides actionable remediation text.

### 4. Third-Party Risk Management (TPRM)
![Vendor Risk Management](screenshots/04_Vendor_Risk_Management.png)
**What it does:** The **Vendor Agent** evaluates third-party suppliers using a weighted scoring model. It considers security certifications (SOC 2, ISO), data access sensitivity (PII/PHI), and incident history to automatically generate a Risk Tier and Score out of 100, visually mapped onto a risk distribution chart.

### 5. Audit & Incident Response
![Audit Readiness](screenshots/05_Audit_Incident_Response.png)
**What it does:** The **Audit Agent** utilizes the Microsoft Graph API to continuously pull tenant evidence (MFA statuses, conditional access policies) and map them to compliance frameworks to generate a real-time "Readiness Score." It is coupled with the Incident Response workflow that tracks threats through a state machine (Triaging → Investigating → Containing).

### 6. Architecture & Data Flow
![Architecture Overview](screenshots/06_Architecture_Overview.png)
**What it does:** A visual overview of the three proprietary IQ layers that power SecureCopilot 365:
- **Work IQ**: Provides organizational context (user roles, departments).
- **Foundry IQ**: The RAG pipeline connecting agents to the knowledge base.
- **Fabric IQ**: The semantic ontology layer mapping threats to compliance controls.
