from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./jobminer.db"
    groq_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()