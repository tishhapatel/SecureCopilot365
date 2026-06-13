targetScope = 'subscription'

param location string = 'eastus'
param resourceGroupName string = 'rg-securecopilot365'
param appName string = 'securecop365'

// Resource naming parameters
var backendAppName = 'app-${appName}-backend-${uniqueString(resourceGroup.id)}'
var frontendAppName = 'app-${appName}-frontend-${uniqueString(resourceGroup.id)}'
var botAppName = 'app-${appName}-bot-${uniqueString(resourceGroup.id)}'
var sqlServerName = 'sql-${appName}-${uniqueString(resourceGroup.id)}'
var openAiName = 'cog-${appName}-openai-${uniqueString(resourceGroup.id)}'
var searchName = 'srch-${appName}-${uniqueString(resourceGroup.id)}'
var keyVaultName = 'kv-${appName}-${uniqueString(resourceGroup.id)}'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
}

@secure()
param administratorLoginPassword string

module resources './resources.bicep' = {
  name: 'securecopilot-deploy'
  scope: resourceGroup
  params: {
    location: location
    backendAppName: backendAppName
    frontendAppName: frontendAppName
    botAppName: botAppName
    sqlServerName: sqlServerName
    openAiName: openAiName
    searchName: searchName
    keyVaultName: keyVaultName
    administratorLoginPassword: administratorLoginPassword
  }
}
