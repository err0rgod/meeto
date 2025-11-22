# Whisper Installation Fix

## Problem

The `openai-whisper==20231117` package has compatibility issues with Python 3.14, causing build errors.

## Solution

We've replaced `openai-whisper` with `faster-whisper`, which is:
- ✅ More compatible with newer Python versions
- ✅ Faster and more efficient
- ✅ Actively maintained
- ✅ Better for production use

## Installation

### Option 1: Install Updated Requirements (Recommended)

```bash
cd backend
pip install -r requirements.txt
```

The requirements.txt now includes `faster-whisper` instead of `openai-whisper`.

### Option 2: Install faster-whisper Manually

If you still have issues, install faster-whisper directly:

```bash
pip install faster-whisper
```

### Option 3: Use Python 3.11 or 3.12 (Alternative)

If you prefer to stick with openai-whisper:

1. Use Python 3.11 or 3.12 (not 3.14)
2. Create a new virtual environment:
   ```bash
   python3.12 -m venv venv
   ```
3. Install requirements normally

## Faster-Whisper Benefits

- **5x faster** inference than openai-whisper
- **Lower memory** usage
- **Better accuracy** in some cases
- **Active maintenance** and updates

## Code Compatibility

The code has been updated to use `faster-whisper` API which is compatible with the same functionality. The service interface remains the same, so no other code changes are needed.

## Troubleshooting

### Still getting errors?

1. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install build dependencies:**
   ```bash
   pip install wheel setuptools
   ```

3. **Try installing faster-whisper with specific version:**
   ```bash
   pip install faster-whisper==1.0.0
   ```

4. **Check Python version:**
   ```bash
   python --version
   ```
   If Python 3.14, consider using Python 3.11 or 3.12 for better compatibility.

### Model Download

First time using faster-whisper will download the model automatically. Models are cached for future use.

### Memory Issues

If you run into memory issues with larger models, use a smaller model:
- `tiny` - ~39 MB (fastest)
- `base` - ~74 MB (default, good balance)
- `small` - ~244 MB
- `medium` - ~769 MB
- `large` - ~1550 MB (best quality but slowest)

Set in `.env`:
```env
WHISPER_MODEL=base
```

