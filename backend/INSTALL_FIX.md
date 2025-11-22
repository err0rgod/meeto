# Quick Fix for Installation Errors

## Problem 1: DATABASE_URL Error ✅ FIXED

The config now ignores extra fields, so `DATABASE_URL` in `.env` won't cause errors anymore.

**Optional cleanup:** You can remove it from `.env` manually, but it's not required.

## Problem 2: Rust/Cargo Error with pydantic-core

**Root Cause:** Python 3.14 is too new. `pydantic-core` needs to compile from source and requires Rust.

## Solution: Use Python 3.12 (Recommended)

**This is the easiest fix!**

### Step 1: Install Python 3.12

1. Download Python 3.12 from: https://www.python.org/downloads/
2. Install it (check "Add Python to PATH")

### Step 2: Create New Virtual Environment with Python 3.12

```powershell
# Find Python 3.12 path (if installed)
py -3.12 -m venv venv

# Or use full path:
C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe -m venv venv

# Activate
venv\Scripts\activate
```

### Step 3: Install Requirements

```bash
pip install -r requirements.txt
```

This should work without Rust errors!

## Alternative: Install Rust (If you want to stick with Python 3.14)

1. Go to: https://rustup.rs/
2. Download and run installer
3. Restart terminal
4. Install requirements again

## Quick Test After Fix

```bash
# Start server
python run.py

# Should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

If you see that, everything works! 🎉

