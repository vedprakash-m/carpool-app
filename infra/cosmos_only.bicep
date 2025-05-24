// Cosmos DB only deployment template
param location string = 'westus'
param resourcePrefix string = 'vcarpool'
param environment string = 'dev'

// Cosmos DB Account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: '${resourcePrefix}-${environment}-cosmos'
  location: location
  tags: {
    Environment: environment
    Project: 'Carpool-Management'
  }
  kind: 'GlobalDocumentDB'
  properties: {
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    databaseAccountOfferType: 'Standard'
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    backup: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
      }
    }
  }
}

// Cosmos DB Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosAccount
  name: 'carpool_db'
  properties: {
    resource: {
      id: 'carpool_db'
    }
  }
}

// Users Container
resource usersContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'users'
  properties: {
    resource: {
      id: 'users'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

// Children Container
resource childrenContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'children'
  properties: {
    resource: {
      id: 'children'
      partitionKey: {
        paths: ['/parent_id']
        kind: 'Hash'
      }
    }
  }
}

// Locations Container
resource locationsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'locations'
  properties: {
    resource: {
      id: 'locations'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

// Weekly Schedule Template Slots Container
resource weeklyScheduleContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'weekly_schedule_template_slots'
  properties: {
    resource: {
      id: 'weekly_schedule_template_slots'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

// Driver Weekly Preferences Container
resource driverPreferencesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'driver_weekly_preferences'
  properties: {
    resource: {
      id: 'driver_weekly_preferences'
      partitionKey: {
        paths: ['/driver_parent_id']
        kind: 'Hash'
      }
    }
  }
}

// Ride Assignments Container
resource rideAssignmentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: cosmosDatabase
  name: 'ride_assignments'
  properties: {
    resource: {
      id: 'ride_assignments'
      partitionKey: {
        paths: ['/id']
        kind: 'Hash'
      }
    }
  }
}

// Outputs
output cosmosAccountName string = cosmosAccount.name
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
output databaseName string = cosmosDatabase.name
