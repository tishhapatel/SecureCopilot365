# SecureCopilot 365 Diagrams

This folder contains the system architecture and logic flow diagrams for **SecureCopilot 365**.

All diagrams are built using [Mermaid.js](https://mermaid.js.org/) so they render natively directly inside GitHub.

## Diagrams Directory

1. [Multi-Agent Query Flow](./01-multi-agent-query-flow.md)
   - Visualizes how the Orchestrator routes incoming requests to the domain-specific sub-agents and handles fallbacks.

2. [Zero Trust Continuous Authorization](./02-zero-trust-authorization.md)
   - Outlines the 6-gate authentication pipeline, continuous runtime authorization, and the underlying data security layers.

3. [Multi-Tenant Isolation Boundaries](./03-multi-tenant-isolation.md)
   - Details how tenant context is injected and strictly isolated across the API layer, Agent execution layer, and Database row-level security.

4. [High-Level System Architecture](./04-high-level-architecture.md)
   - The primary 4-tier layer model (Client, API/Middleware, Agent, Data/Integration).

5. [Microsoft 365 Copilot Integration Topology](./05-m365-copilot-integration.md)
   - Shows the specific hooks into the M365 Ecosystem, including Teams, SharePoint, and Microsoft Graph API via the Agent Plugin Layer.
