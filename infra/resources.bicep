param location string
param backendAppName string
param frontendAppName string
param botAppName string
param sqlServerName string
param openAiName string
param searchName string
param keyVaultName string

// 1. App Service Plan (Linux)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'plan-securecop365'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// 2. Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
}

// 3. Cognitive Service (Azure OpenAI)
resource openAiService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAiName
  }
}

// Deployments for OpenAI
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiService
  name: 'gpt-4o'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiService
  name: 'text-embedding-3-large'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-large'
      version: '1'
    }
  }
}

// 4. Azure AI Search Service
resource searchService 'Microsoft.Search/searchServices@2022-09-01' = {
  name: searchName
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
  }
}

// 5. Azure SQL Database
resource sqlServer 'Microsoft.Sql/servers@2021-11-01' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'SuperSecurePass123!' // Replace in production/KV
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2021-11-01' = {
  parent: sqlServer
  name: 'db-securecop365'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
}

// Allow Azure Services access to SQL Server
resource firewallRules 'Microsoft.Sql/servers/firewallRules@2021-11-01' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// 6. Backend Web App (FastAPI)
resource backendApp 'Microsoft.Web/sites@2022-03-01' = {
  name: backendAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'APP_ENV'
          value: 'production'
        }
        {
          name: 'DATABASE_URL'
          value: 'mssql+pyodbc://sqladmin:SuperSecurePass123!@${sqlServer.properties.fullyQualifiedDomainName}/db-securecop365?driver=ODBC+Driver+18+for+SQL+Server'
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAiService.properties.endpoint
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
          value: 'gpt-4o'
        }
        {
          name: 'AZURE_SEARCH_ENDPOINT'
          value: 'https://${searchService.name}.search.windows.net'
        }
      ]
    }
  }
}

// 7. Teams Bot Web App (Node.js)
resource botApp 'Microsoft.Web/sites@2022-03-01' = {
  name: botAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appSettings: [
        {
          name: 'BACKEND_API_URL'
          value: 'https://${backendApp.name}.azurewebsites.net/api/v1'
        }
      ]
    }
  }
}

// 8. Frontend Web App (React Nginx container or Node runtime)
resource frontendApp 'Microsoft.Web/sites@2022-03-01' = {
  name: frontendAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appSettings: [
        {
          name: 'VITE_BACKEND_API_URL'
          value: 'https://${backendApp.name}.azurewebsites.net/api/v1'
        }
      ]
    }
  }
}
