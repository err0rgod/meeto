"""
Whisper service for speech-to-text conversion
Uses OpenAI Whisper API (no local installation needed)
"""
from typing import Optional, Dict, Any
from app.config import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class WhisperService:
    """Service for transcribing audio using OpenAI Whisper API"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not set. Get one from https://platform.openai.com/api-keys"
            )
        
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def transcribe(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI Whisper API

        Args:
            audio_file_path: Path to audio file

        Returns:
            Dictionary with transcript and metadata
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Extract segments if available
            segments = []
            if hasattr(transcript, 'segments'):
                segments = transcript.segments
            elif isinstance(transcript, dict) and 'segments' in transcript:
                segments = transcript['segments']
            
            return {
                "text": transcript.text,
                "language": getattr(transcript, 'language', 'unknown'),
                "segments": segments,
                "full_result": transcript.model_dump() if hasattr(transcript, 'model_dump') else str(transcript)
            }
        except Exception as e:
            raise RuntimeError(f"Error transcribing audio with OpenAI Whisper: {str(e)}")


# Initialize service if OpenAI API key is available
whisper_service = None
if settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
    try:
        whisper_service = WhisperService()
    except Exception as e:
        print(f"Warning: Could not initialize Whisper service: {e}")
