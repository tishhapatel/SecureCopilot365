# SecureCopilot 365 — Multi-Tenant Isolation Boundaries

This diagram showcases how data and processing streams are isolated per tenant from API request down to the database schema level.

```mermaid
flowchart TD
    subgraph Incoming Request Path
        direction LR
        TA[Tenant A Request]
        TB[Tenant B Request]
        TC[Tenant C Request]
        TA & TB & TC --> Entra[Entra ID Auth<br/>JWT claims: tid, oid, roles] --> Context[Tenant Context Injection]
    end

    subgraph Application / API Layer
        direction LR
        Router[FastAPI Router<br/>Route + RBAC check] --> DI[Dependency Injection<br/>tenant_id from JWT]
        DI --> Rate[Rate Limiter<br/>Per tenant sliding window] --> Audit[Audit Logger<br/>tenant_id on every event] --> Corr[Correlation ID Scope]
    end
    
    Context -.->|inject tenant ctx| DI

    subgraph Agent Execution Layer
        direction LR
        Base[BaseAgent<br/>call_llm injects tenant context] --> Azure[Azure OpenAI<br/>Per-tenant system prompt prefix]
        Azure --> Sanitize[Input Sanitizer<br/>sanitize_input] --> Filter[Output Filter<br/>No cross-tenant data leakage] --> ContextWall[LLM Context Wall]
    end

    DI -->|tenant_id propagates| Azure

    subgraph Database Layer
        direction LR
        subgraph Tenant A Schema
            RLS_A[RLS Policy] --- TID_A[tenant_id index]
        end
        subgraph Tenant B Schema
            RLS_B[RLS Policy] --- TID_B[tenant_id index]
        end
        subgraph Tenant C Schema
            RLS_C[RLS Policy] --- TID_C[tenant_id index]
        end
        
        DB[PostgreSQL Engine<br/>Shared cluster]
        Redis[Redis Cluster<br/>Namespaced Keys]
    end
    
    Azure -.->|schema-scoped query| Tenant B Schema
```
