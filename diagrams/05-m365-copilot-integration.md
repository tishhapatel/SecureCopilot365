# SecureCopilot 365 — Microsoft 365 Copilot Integration Topology

This diagram details how SecureCopilot 365 integrates natively into the Microsoft 365 ecosystem via plugins, adaptive cards, and the Microsoft Graph API.

```mermaid
flowchart TD
    subgraph Microsoft 365 Ecosystem
        Copilot[M365 Copilot<br/>Chat / Compose]
        Teams[Teams<br/>Channels / Bots]
        Graph[Graph API]
        SharePoint[SharePoint<br/>Document Store]
        Outlook[Outlook<br/>Email / Calendar]
        
        Copilot <--> Teams
        Teams <--> Graph
        Outlook <--> Graph
        SharePoint <--> Graph
    end

    subgraph Agent Plugin Layer
        Plugin[Copilot Plugin<br/>manifest.json / OAuth]
        Cards[Adaptive Cards<br/>Action Responses]
    end

    Copilot -->|invoke| Plugin

    subgraph SecureCopilot 365 Backend Azure
        Bot[Bot Framework<br/>Adapter / Connector]
        API[FastAPI<br/>REST + WebSocket]
        Entra[Entra ID<br/>Auth / JWT]
        
        Orch[Orchestrator<br/>LLM Router]
        Agents[Sub-Agents<br/>Phishing, Compliance, Vendor, Audit, Awareness]
        
        PG[PostgreSQL<br/>Tenant DB]
        Redis[Redis<br/>Rate / Cache]
        OpenAI[Azure OpenAI<br/>GPT-4o]
        
        Blob[Blob Storage<br/>Evidence / Audit]
        KV[Key Vault<br/>Secrets / Certs]
        AppIns[App Insights<br/>Telemetry]
        
        Bot <--> API
        API --> Entra
        Bot --> Orch
        Orch --> Agents
        Agents --> PG & Redis & OpenAI
        PG --> Blob
        Redis --> KV
        OpenAI --> AppIns
    end

    Teams <--> Bot
    Plugin --> API
    Cards --> Bot
    Graph <--> Agents
```
