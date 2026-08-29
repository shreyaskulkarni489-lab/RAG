import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campusmind.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretjwtkeychangeinproduction12345")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_LOCAL_EMBEDDINGS: bool = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
