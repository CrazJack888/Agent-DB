import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://agent:agentpass@localhost:5432/agent_db"
    sync_database_url: str = "postgresql://agent:agentpass@localhost:5432/agent_db"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
