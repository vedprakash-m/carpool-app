from azure.cosmos import CosmosClient, PartitionKey
from app.core.config import get_settings

settings = get_settings()

def get_cosmos_client():
    client = CosmosClient(settings.COSMOS_ENDPOINT, settings.COSMOS_KEY)
    return client

def get_database():
    client = get_cosmos_client()
    database = client.get_database_client(settings.COSMOS_DATABASE)
    return database

def init_cosmos_db():
    """Initialize Cosmos DB with required containers if they don't exist"""
    client = get_cosmos_client()
    try:
        database = client.create_database_if_not_exists(id=settings.COSMOS_DATABASE)
        
        # Create containers with appropriate partition keys
        database.create_container_if_not_exists(
            id="users",
            partition_key=PartitionKey(path="/id")
        )
        
        database.create_container_if_not_exists(
            id="children",
            partition_key=PartitionKey(path="/parent_id")
        )
        
        database.create_container_if_not_exists(
            id="locations",
            partition_key=PartitionKey(path="/id")
        )
        
        database.create_container_if_not_exists(
            id="weekly_schedule_template_slots",
            partition_key=PartitionKey(path="/id")
        )
        
        database.create_container_if_not_exists(
            id="driver_weekly_preferences",
            partition_key=PartitionKey(path="/driver_parent_id")
        )
        
        database.create_container_if_not_exists(
            id="ride_assignments",
            partition_key=PartitionKey(path="/driver_parent_id")
        )
        
        database.create_container_if_not_exists(
            id="swap_requests",
            partition_key=PartitionKey(path="/requesting_driver_id")
        )
        
    except Exception as e:
        print(f"Error initializing Cosmos DB: {str(e)}")
        raise

def get_container(container_name: str):
    """Get a container client by name"""
    database = get_database()
    container = database.get_container_client(container_name)
    return container 