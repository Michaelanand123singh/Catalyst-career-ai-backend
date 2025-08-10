from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    # App
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API keys / Models
    GOOGLE_API_KEY: str = ""
    # Text generation model. Accepts values like:
    # - "gemini-1.5-flash" (recommended)
    # - "1.5-flash" (will be normalized)
    # - "gemini/gemini-1.5-flash" (will be used as-is)
    GEMINI_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"

    # RAG / Vector DB
    DOCUMENTS_PATH: str = "data/career_documents"
    CHROMA_DB_PATH: str = "data/vector_db"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    VECTOR_SEARCH_K: int = 4
    SCORE_THRESHOLD: float = 0.6

    # Generation parameters
    TEMPERATURE: float = 0.4
    MAX_TOKENS: int = 1024

    # pydantic-settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate settings once for app-wide use
settings = Settings()