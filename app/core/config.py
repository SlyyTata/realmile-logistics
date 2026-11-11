from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Realmile Logistics API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database config
    DATABASE_URL: str
    
    # Security config
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Deployment config
    # Comma-separated list of frontend origins allowed to call the API (CORS)
    CORS_ORIGINS: str = "http://localhost:3000"
    # Log every SQL statement (development only)
    DEBUG: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # Tells Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instantiate it so we can import 'settings' anywhere in our code
settings = Settings()