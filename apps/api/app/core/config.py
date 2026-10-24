import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = "Grievance360 API"
    VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("API_PORT", "8000"))
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres_secret_password@localhost:5432/grievance360_db",
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
