"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    model_config = {
        "extra": "ignore",  # Ignore extra fields in .env (like old DATABASE_URL)
        "env_file": ".env",
        "case_sensitive": True
    }
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Groq API (for LLM extraction)
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    
    # AssemblyAI (for Transcription)
    ASSEMBLYAI_API_KEY: Optional[str] = None
    
    # Local Application Mode
    ENABLE_LOCAL_MODE: bool = False
    
    # Jira Integration
    JIRA_BASE_URL: Optional[str] = None
    JIRA_EMAIL: Optional[str] = None
    JIRA_API_TOKEN: Optional[str] = None
    
    # File upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_FORMATS: List[str] = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    
    # Storage
    UPLOAD_DIR: str = "./uploads"


# Initialize settings - catch any errors
try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Error loading settings: {e}")
    print("Using default settings...")
    # Create minimal settings if pydantic fails
    class SimpleSettings:
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        CORS_ORIGINS = ["*"]
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
        ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
        ENABLE_LOCAL_MODE = os.getenv("ENABLE_LOCAL_MODE", "False").lower() == "true"
        JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
        JIRA_EMAIL = os.getenv("JIRA_EMAIL")
        JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
        MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))
        ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
        UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    settings = SimpleSettings()
