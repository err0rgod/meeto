import assemblyai as aai
from app.config import settings

class AssemblyAIService:
    def __init__(self):
        if not settings.ASSEMBLYAI_API_KEY:
            raise ValueError("ASSEMBLYAI_API_KEY is not set")
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        self.transcriber = aai.Transcriber()

    def transcribe(self, file_path: str) -> dict:
        """
        Transcribe audio file using AssemblyAI
        Returns dict with 'text' key to match previous interface
        """
        try:
            transcript = self.transcriber.transcribe(file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
                
            return {
                "text": transcript.text,
                "id": transcript.id,
                "status": transcript.status
            }
        except Exception as e:
            print(f"AssemblyAI Error: {e}")
            raise

# Singleton
try:
    assemblyai_service = AssemblyAIService()
except Exception as e:
    print(f"Warning: AssemblyAI service not initialized: {e}")
    assemblyai_service = None
