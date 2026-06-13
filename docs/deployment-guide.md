# Azure Deployment Guide — SecureCopilot 365

This document explains how to deploy SecureCopilot 365 to Azure using Bicep templates and configure production security services.

---

## 1. Deployment Topology

SecureCopilot 365 is deployed using Azure Container Apps (ACA) within a private virtual network.

```
                                [ Public Access ]
                                        │
                                        ▼
                            [ Azure Front Door + WAF ]
                                        │
                                        ▼
                            [ Azure API Management ]
                                        │
                                        ▼
                        [ Azure Container Apps Network ]
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
        [ Backend ACA - FastAPI ]                [ Frontend ACA - React ]
                     │
         ( Managed Identity authentication )
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
 [ Azure Key Vault ]    [ Azure SQL Database ]
```

---

## 2. Infrastructure Deployment (Bicep)

The infrastructure is defined as Bicep templates within the `/infra` folder:
*   [main.bicep](file:///d:/SecureCopilot365/infra/main.bicep): The main deployment file.
*   [resources.bicep](file:///d:/SecureCopilot365/infra/resources.bicep): Configures Azure SQL Databases, Key Vaults, Container App environments, and Azure OpenAI resources.

### 2.1 Deployment Steps
1.  **Configure Parameters**: Update [main.parameters.json](file:///d:/SecureCopilot365/infra/main.parameters.json) with your environment variables (such as subscription details, resource group name, and location).
2.  **Deploy Resources**: Run the Azure CLI command from the repository root:
    ```bash
    az deployment sub create --location eastus --template-file infra/main.bicep --parameters infra/main.parameters.json
    ```

---

## 3. Post-Deployment Configurations

### 3.1 Managed Identities
*   **System-Assigned Identities**: The backend Container App is configured with a system-assigned managed identity.
*   **Access Control**: Configure access policies on the Azure Key Vault and SQL Server to allow authentication from the backend identity, deprecating the use of connection string secrets in backend configuration profiles.

### 3.2 SQL Database Schema & RLS Setup
1.  **Deploy Schema**: Run database migrations to provision the schema tables.
2.  **Apply Row-Level Security (RLS)**: Execute [rls.sql](file:///d:/SecureCopilot365/apps/backend/db/rls.sql) to apply database security policies to user, employee, and vendor tables.

### 3.3 Entra ID App Registrations
1.  **Register Application**: Register an application in Microsoft Entra ID to support OIDC Single Sign-On.
2.  **Grant API Permissions**: Request admin consent for the required Microsoft Graph API scopes:
    *   `Mail.Read`, `Chat.Read`, `Calendars.Read`, `Files.Read.All`, and `Sites.Read.All`
