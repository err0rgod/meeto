"""
Quick test script to verify services are working
"""
print("Testing services...")

# Test Groq
try:
    from groq import Groq
    print("✅ Groq module imported successfully")
except ImportError as e:
    print(f"❌ Groq module not found: {e}")
    print("   Install with: pip install groq")

# Test Whisper
try:
    from faster_whisper import WhisperModel
    print("✅ faster-whisper module imported successfully")
except ImportError as e:
    print(f"❌ faster-whisper module not found: {e}")
    print("   Install with: pip install faster-whisper")

# Test OpenAI (optional)
try:
    from openai import OpenAI
    print("✅ OpenAI module imported successfully")
except ImportError:
    print("⚠️  OpenAI module not found (optional - only needed for Whisper API)")

# Test Jira service
try:
    from app.services.jira_service import JiraService
    print("✅ Jira service imported successfully")
except Exception as e:
    print(f"❌ Jira service error: {e}")

# Test config
try:
    from app.config import settings
    print("✅ Config loaded successfully")
    print(f"   GROQ_API_KEY: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
    print(f"   JIRA_BASE_URL: {'Set' if settings.JIRA_BASE_URL else 'Not set'}")
except Exception as e:
    print(f"❌ Config error: {e}")

print("\nIf all checks passed, you're ready to run the server!")

