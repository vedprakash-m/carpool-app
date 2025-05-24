// Carpool Management Application Infrastructure with Cosmos DB
// This Bicep template defines the Azure resources needed for the Carpool Management application

// Parameters
@description('The name prefix used for all resources')
param resourcePrefix string = 'vcarpool'

@description('The location for all resources')
param location string = resourceGroup().location

@description('The environment (dev, test, prod)')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('The SKU for the App Service plan')
param appServicePlanSku string = 'B1'

@description('The runtime stack for the Web App')
param webAppRuntimeStack string = 'PYTHON:3.12'

@description('Enable RBAC authorization for Key Vault')
param keyVaultEnableRbacAuthorization bool = true

// Variables
var resourceToken = '${resourcePrefix}-${environment}'
var appServicePlanName = '${resourceToken}-plan'
var webAppName = '${resourceToken}-api'
var keyVaultName = '${resourceToken}-vault'
var staticWebAppName = '${resourceToken}-frontend'
var cosmosDbAccountName = '${resourceToken}-cosmos'
var cosmosDbDatabaseName = 'carpool_db'
var tags = {
  azd_env_name: resourceToken
  application: 'Carpool Management'
  environment: environment
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: appServicePlanSku
  }
  properties: {
    reserved: true // Required for Linux
  }
}

// Cosmos DB Account
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosDbAccountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

// Cosmos DB Database
resource cosmosDbDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDbAccount
  name: cosmosDbDatabaseName
  properties: {
    resource: {
      id: cosmosDbDatabaseName
    }
  }
}

// Cosmos DB Containers
resource usersContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'users'
  properties: {
    resource: {
      id: 'users'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

resource childrenContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'children'
  properties: {
    resource: {
      id: 'children'
      partitionKey: {
        paths: ['/parent_id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

resource locationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'locations'
  properties: {
    resource: {
      id: 'locations'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

resource weeklyScheduleContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'weekly_schedule_template_slots'
  properties: {
    resource: {
      id: 'weekly_schedule_template_slots'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

resource driverPreferencesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'driver_weekly_preferences'
  properties: {
    resource: {
      id: 'driver_weekly_preferences'
      partitionKey: {
        paths: ['/driver_parent_id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

resource rideAssignmentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDbDatabase
  name: 'ride_assignments'
  properties: {
    resource: {
      id: 'ride_assignments'
      partitionKey: {
        paths: ['/driver_parent_id']
        kind: 'Hash'
      }
      defaultTtl: -1
    }
  }
}

// Web App for Backend
resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppName
  location: location
  tags: union(tags, {
    azd_service_name: 'api'
  })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: webAppRuntimeStack
      alwaysOn: true
      cors: {
        allowedOrigins: ['*']
        supportCredentials: true
      }
      appSettings: [
        {
          name: 'COSMOS_ENDPOINT'
          value: '@Microsoft.KeyVault(SecretUri=https://${keyVault.name}.vault.azure.net/secrets/COSMOS-ENDPOINT/)'
        }
        {
          name: 'COSMOS_KEY'
          value: '@Microsoft.KeyVault(SecretUri=https://${keyVault.name}.vault.azure.net/secrets/COSMOS-KEY/)'
        }
        {
          name: 'COSMOS_DATABASE'
          value: cosmosDbDatabaseName
        }
        {
          name: 'JWT_SECRET_KEY'
          value: '@Microsoft.KeyVault(SecretUri=https://${keyVault.name}.vault.azure.net/secrets/JWT-SECRET-KEY/)'
        }
        {
          name: 'WEBSITE_WEBDEPLOY_USE_SCM'
          value: 'true'
        }
      ]
    }
    httpsOnly: true
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    enableRbacAuthorization: keyVaultEnableRbacAuthorization
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: 'centralus'  // Static Web Apps requires specific regions
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    buildProperties: {
      appLocation: 'frontend'
      apiLocation: ''
      outputLocation: '.next'
      appBuildCommand: 'npm run build'
    }
  }
}

// Key Vault Role Assignment for Web App's Managed Identity
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, webApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output webAppName string = webApp.name
output webAppHostName string = webApp.properties.defaultHostName
output webAppId string = webApp.id
output keyVaultName string = keyVault.name
output staticWebAppName string = staticWebApp.name
output staticWebAppHostName string = staticWebApp.properties.defaultHostname
output staticWebAppId string = staticWebApp.id
output cosmosDbAccountName string = cosmosDbAccount.name
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint
output cosmosDbDatabaseName string = cosmosDbDatabaseName
