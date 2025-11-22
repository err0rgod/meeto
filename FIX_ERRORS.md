# Fixing Common Errors

## Error 1: "Extra inputs are not permitted" - DATABASE_URL

**Problem:** Your `.env` file still has `DATABASE_URL` but the system no longer uses a database.

**Fix:**
1. Open `backend/.env` file
2. Remove or comment out the `DATABASE_URL` line:
   ```env
   # DATABASE_URL=... (remove this line or comment it out)
   ```
3. Save and restart the server

**Alternative:** The config is now set to ignore extra fields, so this shouldn't cause errors anymore.

## Error 2: "Rust/Cargo not found" - pydantic-core build error

**Problem:** `pydantic-core` needs Rust to compile, but Rust isn't properly installed or on PATH.

**Solution 1: Install Rust (Recommended)**

1. Install Rust from: https://rustup.rs/
2. Or on Windows with chocolatey:
   ```powershell
   choco install rust
   ```
3. Restart terminal and try again

**Solution 2: Use Pre-built Wheel (Easier)**

Try installing pydantic with a pre-built wheel:

```bash
pip install --only-binary :all: pydantic pydantic-settings
```

**Solution 3: Use Python 3.11 or 3.12 (Best for compatibility)**

Python 3.14 is very new and some packages don't have pre-built wheels yet:

1. Install Python 3.11 or 3.12
2. Create new virtual environment:
   ```bash
   python3.12 -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

**Solution 4: Skip pydantic validation temporarily**

If you need to run immediately, you can modify config.py to use basic settings:

```python
import os

# Simple config without pydantic (temporary)
class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    USE_LOCAL_WHISPER = os.getenv("USE_LOCAL_WHISPER", "true").lower() == "true"
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "100000000"))
    ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]

settings = Settings()
```

## Quick Fix Steps

1. **Remove DATABASE_URL from .env:**
   ```bash
   # Edit backend/.env and remove DATABASE_URL line
   ```

2. **Try installing with pre-built wheels:**
   ```bash
   pip install --only-binary :all: -r requirements.txt
   ```

3. **If that fails, use Python 3.11/3.12:**
   ```bash
   # Use Python 3.11 or 3.12 instead of 3.14
   python3.12 -m venv venv
   ```

## Check Your .env File

Make sure your `backend/.env` looks like this:

```env
# Groq API
GROQ_API_KEY=your-groq-api-key

# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token

# Whisper
WHISPER_MODEL=base
USE_LOCAL_WHISPER=true

# Remove or comment out this line:
# DATABASE_URL=...  <- DELETE THIS
```

## Still Having Issues?

1. **Delete your .env file and recreate it** with only the needed values
2. **Use Python 3.11 or 3.12** for better package compatibility
3. **Install Rust** if you want to use Python 3.14

