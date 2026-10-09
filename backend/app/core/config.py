"""
Application configuration — loaded from .env
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./voicebiz.db"

    # Casjoe Biz
    CASJOE_API_BASE_URL: str = "https://app.casjoe.com/api/v1"
    CASJOE_JWT_SECRET: str = ""

    # N-ATLAS / Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    N_ATLAS_MODEL: str = "hf.co/QuantFactory/N-ATLaS-GGUF:Q4_K_M"

    # N-ATLAS HF endpoint (demo fallback)
    NATLAS_ENDPOINT: str = ""
    HF_TOKEN: str = ""

    # ASR
    AUDIO_UPLOAD_DIR: str = "./uploads/audio"
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    MAX_AUDIO_DURATION_SECONDS: int = 30

    # HuggingFace Bucket
    HF_BUCKET_REPO: str = "casjoetech/N-ATLaS-bucket"

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SECRET_KEY: str = "change-this-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
