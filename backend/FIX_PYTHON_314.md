# Fixing Python 3.14 Compatibility Issues

## The Problem

You're using **Python 3.14** which is very new. Some packages like `pydantic-core` need to be compiled from source and require Rust, which isn't properly set up.

## Quick Fix Options

### Option 1: Use Pre-built Wheels (Easiest)

Try installing with pre-built wheels only:

```bash
pip install --only-binary :all: -r requirements.txt
```

If that doesn't work, try installing pydantic separately:

```bash
pip install --only-binary :all: pydantic pydantic-settings
pip install -r requirements.txt --no-deps
pip install fastapi uvicorn groq faster-whisper requests python-multipart python-dotenv
```

### Option 2: Use Python 3.11 or 3.12 (Recommended)

Python 3.14 is too new - most packages don't have pre-built wheels yet.

**Steps:**

1. **Install Python 3.12** (or 3.11):
   - Download from: https://www.python.org/downloads/
   - Or use `pyenv` if you have it

2. **Create new virtual environment with Python 3.12:**
   ```powershell
   # Find Python 3.12 path (usually something like):
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
   
   # Or if Python 3.12 is in PATH:
   py -3.12 -m venv venv
   
   # Activate
   venv\Scripts\activate
   ```

3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 3: Install Rust (For Python 3.14)

If you want to stick with Python 3.14:

1. **Install Rust:**
   - Go to: https://rustup.rs/
   - Download and run the installer
   - Or use chocolatey: `choco install rust`

2. **Restart your terminal** after installing Rust

3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 4: Use Simple Config (Workaround)

I've updated `config.py` to handle errors gracefully. If pydantic fails, it will use a simple settings class.

The config will automatically fall back if pydantic can't load, so you can still run the server!

## Fix DATABASE_URL Error

Your `.env` file still has `DATABASE_URL` which is no longer needed. I've configured the settings to **ignore extra fields**, so this won't cause errors anymore.

However, you can still clean up your `.env`:

```env
# Remove or comment out this line:
# DATABASE_URL=postgresql://...

# Keep only these:
GROQ_API_KEY=your-groq-api-key
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token
WHISPER_MODEL=base
USE_LOCAL_WHISPER=true
```

## Recommended Solution

**Use Python 3.12** - It's the most stable for this project and all packages have pre-built wheels.

```powershell
# Check what Python versions you have
py --list

# Use Python 3.12
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Testing After Fix

1. Start server:
   ```bash
   python run.py
   ```

2. Check if it starts without errors:
   - Should see: "Uvicorn running on http://0.0.0.0:8000"

3. Test the endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

If you see `{"status": "healthy"}`, you're good to go!

