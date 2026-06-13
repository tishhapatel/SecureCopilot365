# Foundry IQ — GRC Knowledge Retrieval

This document explains the architecture, search indexing, and security isolation of the **Foundry IQ** RAG (Retrieval-Augmented Generation) layer.

---

## 1. System Overview

Foundry IQ is the knowledge retrieval engine for SecureCopilot 365. It provides domain-specific cybersecurity and compliance context (such as ISO 27001, GDPR, and NIST guidelines) to domain agents.

```
[Agent Query] 
     │
     ▼
[FoundryIQ.retrieve()]
     │
     ├──► (With Azure Search Credentials) ──► Query Azure AI Search index
     │
     └──► (Without Credentials Fallback) ──► Local JSON keyword scoring
                                                       │
                                            [ RAG Chunk-Level ACL check ]
                                                       │
                                                       ▼
                                            [ Authorized context blocks ]
```

---

## 2. Technical Specifications

### 2.1 Azure AI Search Integration
In production, Foundry IQ connects to an Azure AI Search index (`AZURE_SEARCH_INDEX_NAME`). It uses the Azure OpenAI `text-embedding-3-large` deployment to vectorize queries and retrieve relevant framework document chunks.

### 2.2 Local JSON Fallback Index
To support offline development and testing, Foundry IQ includes a local keyword search implementation. The search files are located in `knowledge-base/sources/`:
*   `iso27001_controls.json`: Contains Annex A controls.
*   `gdpr_articles.json`: Contains personal data processing regulations.
*   `nist_csf2_functions.json`: Contains cybersecurity framework guidelines.
*   `owasp_top10.json`: Contains web application security risks.
*   `mitre_attack.json`: Contains common threat techniques.

---

## 3. RAG Chunk-Level ACL Verification

To prevent unauthorized access to sensitive company policies, Foundry IQ implements chunk-level access control list (ACL) checking:

```python
# ACL verification logic in foundry_iq.py
user_role = user_context.get("role")
item_acl = item.get("acl")

if item_acl:
    # Reject chunk if the user's role is not authorized
    if user_role not in item_acl and user_role != "Super Admin":
        logger.warning(f"RAG ACL Gating: User role '{user_role}' denied access to document chunk.")
        continue
```

*   **Behavior**: Document chunks are tagged with authorized roles (e.g. `["CISO", "Compliance Officer"]`). If a user with a lower role (e.g. `General Employee`) queries the advisor, the system filters out the restricted chunks before generating a response.
