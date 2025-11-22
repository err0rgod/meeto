# Audio to Jira - Simple System

Extract text from audio files and automatically create Jira issues.

## Features

- 🎤 Upload audio file (MP3, WAV, M4A, OGG, FLAC)
- 📝 Extract text using OpenAI Whisper API (speech-to-text)
- 🤖 Extract action items using Groq LLM
- 🎫 Create Jira issues automatically
- 💻 Simple web interface (no installation needed)

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
# OpenAI API (for Whisper transcription - REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key

# Groq API (for action item extraction)
GROQ_API_KEY=your-groq-api-key

# Jira Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
```

### 3. Run Server

```bash
python run.py
```

Server runs on `http://localhost:8000`

## Usage

### Web Interface

Just open `http://localhost:8000` in your browser! The web interface allows you to:
- Upload audio files
- Enter Jira project key
- Select issue type and priority
- View transcript and created Jira issues

### API Usage

Upload audio and create Jira issue via API:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@meeting.mp3" \
  -F "jira_project_key=PROJ" \
  -F "jira_issue_type=Task" \
  -F "jira_priority=Medium"
```

**Form Parameters:**
- `file` (required) - Audio file
- `jira_project_key` (required) - Your Jira project key
- `jira_issue_type` (optional) - Issue type, default: "Task"
- `jira_priority` (optional) - Priority, default: "Medium"

**Response:**
```json
{
  "success": true,
  "transcript": "Full transcript text...",
  "action_items": [
    {
      "description": "Follow up with client",
      "owner": "John Doe",
      "deadline": "2024-01-15",
      "priority": "high"
    }
  ],
  "jira_issues": [
    {
      "key": "PROJ-123",
      "url": "https://your-domain.atlassian.net/browse/PROJ-123"
    }
  ]
}
```

## API Endpoints

### GET /

Simple web interface for uploading audio and creating Jira issues.

### POST /upload

Upload audio file and create Jira issues.

**Parameters:**
- `file` (form-data): Audio file (required)
- `jira_project_key` (form-data): Jira project key (required)
- `jira_issue_type` (form-data): Issue type (optional, default: "Task")
- `jira_priority` (form-data): Priority (optional, default: "Medium")

**Returns:**
- Transcript text
- Extracted action items
- Created Jira issue keys and URLs

### GET /health

Health check endpoint.

## How It Works

1. **Upload audio** → File saved temporarily
2. **OpenAI Whisper transcription** → Audio converted to text via API
3. **Groq LLM extraction** → Action items extracted from transcript
4. **Jira creation** → One issue per action item (or single issue with full transcript)
5. **Cleanup** → Audio file deleted

## Requirements

- Python 3.9+
- OpenAI API key (for Whisper transcription)
- Groq API key (for LLM extraction)
- Jira API token

## Get API Keys

### OpenAI API Key (for Whisper)
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up and create API key
3. Add to `.env` as `OPENAI_API_KEY`

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up and create API key
3. Add to `.env` as `GROQ_API_KEY`

### Jira API Token
**Detailed guide:** See `SETUP_JIRA.md` for step-by-step instructions

**Quick setup:**
1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the token (you'll only see it once!)
4. Add to `backend/.env`:
   ```env
   JIRA_BASE_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_API_TOKEN=ATATT3xFfGF0...your-token-here
   ```

**Note:** Replace values with your actual Jira URL, email, and API token.

## Troubleshooting

### Whisper not working?
- Ensure `OPENAI_API_KEY` is set in `.env`
- Check your OpenAI API key is valid
- Verify you have API credits

### Jira creation fails?
- Verify Jira credentials in `.env`
- Check project key exists
- Ensure API token has permissions

### No action items extracted?
- Check Groq API key is set
- Verify LLM service is working
- Check transcript quality
