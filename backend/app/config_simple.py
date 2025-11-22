"""
Simple configuration without pydantic (fallback if pydantic-core fails to install)
"""
import os
from typing import List, Optional


class Settings:
    """Simple settings class without pydantic"""
    
    def __init__(self):
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        
        # CORS
        self.CORS_ORIGINS = ["*"]
        
        # Groq API (for LLM extraction)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
        
        # Whisper
        self.WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
        use_local = os.getenv("USE_LOCAL_WHISPER", "true").lower()
        self.USE_LOCAL_WHISPER = use_local == "true"
        
        # Jira Integration
        self.JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
        self.JIRA_EMAIL = os.getenv("JIRA_EMAIL")
        self.JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
        
        # File upload
        self.MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))  # 100MB
        # Allow .txt transcripts in addition to audio formats
        self.ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".txt"]
        
        # Storage
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
        # Task extraction tuning
        # Tasks with confidence below this threshold will be filtered out
        self.TASK_CONFIDENCE_THRESHOLD = float(os.getenv("TASK_CONFIDENCE_THRESHOLD", "0.4"))
        # Whether to apply deterministic normalization heuristics to task descriptions
        self.NORMALIZE_TASKS = os.getenv("NORMALIZE_TASKS", "true").lower() == "true"


# Try to use pydantic settings, fallback to simple version
try:
    from app.config import settings
except Exception as e:
    print(f"Warning: Could not load pydantic settings: {e}")
    print("Using simple settings class instead...")
    settings = Settings()

