# Future Roadmap — SecureCopilot 365

This document outlines the development stages and future enhancements planned for the SecureCopilot 365 platform.

---

## 1. Version 1.0 — Hackathon Baseline (Current State)

*   **Multi-Agent System**: Functional orchestrator and domain-specific sub-agents (phishing, compliance, vendor, audit, and coach).
*   **Explainable AI**: Enforces structured JSON formatting schemas (reasoning, evidence, citations).
*   **Multi-Tenant Isolation**: Enforces tenant query filtering at the ORM layer.
*   **IQ Layers**: Integrates GRC frameworks (Foundry), Graph API context (Work), and dependency mapping (Fabric).
*   **Security Gating**: Implements Zero Trust authorization and file upload checks.
*   **Ledger Security**: Implements cryptographically chained audit logs.

---

## 2. Version 1.5 — Cloud Deployment (Short Term)

*   **Secrets Migration**: Integrate Azure Key Vault to store secrets and transition to `DefaultAzureCredential`.
*   **Active Malware Scanning**: Integrate a running ClamAV sidecar to replace simulated malware scanning.
*   **Production Database**: Deploy the SQLite schema to Azure SQL and configure database-level Row-Level Security (RLS).
*   **API Management**: Configure Azure API Management (APIM) to enforce access control and rate-limiting policies.

---

## 3. Version 2.0 — Production SaaS (Medium Term)

*   **Graph Database Integration**: Migrate the Fabric IQ dependency graph from SQL to a graph database (e.g. Neo4j or Azure Cosmos DB Gremlin API).
*   **Vector RAG Engine**: Configure Azure AI Search vector indexes to replace local keyword search in the Foundry IQ layer.
*   **Graph Synchronization**: Implement background Graph API synchronization using change notifications.
*   **Evidence Pack Generation**: Generate PDF compliance evidence reports from the Trust Center.

---

## 4. Version 3.0 — Advanced Governance (Long Term)

*   **Multi-Cloud GRC**: Extend compliance monitoring to include AWS and Google Cloud configurations.
*   **Continuous CSPM**: Implement continuous security posture management checks for Azure services.
*   **AI Policy Compliance**: Add GRC frameworks for auditing AI applications (e.g., ISO 42001, EU AI Act).
*   **Federated Learning**: Integrate privacy-preserving federated learning to refine phishing detection models.
