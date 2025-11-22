# Quick Start - Audio to Jira

Simple system to extract text from audio and create Jira issues.

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env`:

```env
# Groq API (for action item extraction)
GROQ_API_KEY=your-groq-api-key

# Jira Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Whisper (optional)
WHISPER_MODEL=base
USE_LOCAL_WHISPER=true
```

### 3. Run Server

```bash
python run.py
```

Server runs on `http://localhost:8000`

## Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/upload?jira_project_key=PROJ" \
  -F "file=@meeting.mp3"
```

### Using Python

```python
import requests

url = "http://localhost:8000/upload"
files = {"file": open("meeting.mp3", "rb")}
params = {"jira_project_key": "PROJ"}

response = requests.post(url, files=files, params=params)
print(response.json())
```

## Get API Keys

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up and create API key

### Jira API Token
**Full guide:** See `SETUP_JIRA.md` for detailed instructions

**Quick steps:**
1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy token (shown only once!)
4. Find your Jira URL (e.g., `https://company.atlassian.net`)
5. Add to `backend/.env`:
   ```env
   JIRA_BASE_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_API_TOKEN=your-token-here
   ```

## That's it! 🎉

Just upload audio files and they'll automatically become Jira issues.
