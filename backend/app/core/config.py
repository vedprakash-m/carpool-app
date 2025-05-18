from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Carpool Management API"
    
    # Azure Cosmos DB Configuration
    COSMOS_ENDPOINT: str
    COSMOS_KEY: str
    COSMOS_DATABASE: str = "carpool_db"
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Azure Key Vault Configuration
    AZURE_KEYVAULT_URL: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
      # Email Configuration
    EMAIL_NOTIFICATIONS_ENABLED: bool = False  # Set to True to enable email notifications
    SMTP_TLS: bool = True
    SMTP_SERVER: Optional[str] = None  # SMTP server hostname
    SMTP_PORT: Optional[int] = 587  # Default SMTP port with TLS
    SMTP_USERNAME: Optional[str] = None  # SMTP username
    SMTP_PASSWORD: Optional[str] = None  # SMTP password
    FROM_EMAIL: Optional[str] = None  # Sender email address
    FROM_NAME: Optional[str] = "Carpool Management System"  # Sender name

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 