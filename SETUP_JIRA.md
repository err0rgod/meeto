# How to Set Up Jira Integration

This guide will help you configure Jira so the system can automatically create issues from audio transcripts.

## Step 1: Get Your Jira Domain

1. Go to your Jira instance (e.g., `https://yourcompany.atlassian.net`)
2. Copy the base URL - this is your `JIRA_BASE_URL`
   - Example: `https://yourcompany.atlassian.net`
   - Or: `https://jira.yourcompany.com`

## Step 2: Create a Jira API Token

1. **Go to Atlassian Account Settings:**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Or: Go to your Jira → Profile → Account Settings → Security → API tokens

2. **Create API Token:**
   - Click **"Create API token"**
   - Give it a label (e.g., "Audio to Jira")
   - Click **"Create"**
   - **IMPORTANT:** Copy the token immediately - you won't be able to see it again!
   - It looks like: `ATATT3xFfGF0...` (long string)

3. **Save the token securely** - you'll need it for the `.env` file

## Step 3: Get Your Jira Email

Use the email address associated with your Jira account:
- This is the email you use to log in to Jira
- Example: `your.name@company.com`

**Note:** Some Jira instances use username instead of email. If email doesn't work, check with your Jira admin.

## Step 4: Find Your Project Key

1. Go to your Jira project
2. Look at any issue in that project
3. The issue key looks like: `PROJ-123`
4. The part before the dash is your **Project Key** (e.g., `PROJ`)

Or:
1. Go to Project Settings in Jira
2. Look for "Project Key" or "Key"
3. Copy it (usually 2-10 uppercase letters)

## Step 5: Configure Your System

Edit `backend/.env` file:

```env
# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=ATATT3xFfGF0...your-api-token-here
```

**Important:**
- Replace `yourcompany.atlassian.net` with your actual Jira URL
- Replace `your.email@company.com` with your Jira email
- Replace `ATATT3xFfGF0...` with your actual API token

## Step 6: Test the Connection

### Option 1: Test via API

```bash
cd backend
python run.py
```

Then in another terminal:
```bash
# Test with a sample audio file
python test_upload.py meeting.mp3 YOUR_PROJECT_KEY
```

### Option 2: Test via curl

```bash
curl -X POST "http://localhost:8000/upload?jira_project_key=PROJ" \
  -F "file=@meeting.mp3"
```

Replace `PROJ` with your actual project key.

## Troubleshooting

### "Jira credentials not configured" Error

**Problem:** Missing or incorrect Jira configuration

**Solution:**
1. Check `.env` file exists in `backend/` directory
2. Verify all three values are set:
   - `JIRA_BASE_URL`
   - `JIRA_EMAIL`
   - `JIRA_API_TOKEN`
3. Make sure no quotes around values in `.env`
4. Restart the server after changing `.env`

### "401 Unauthorized" Error

**Problem:** Invalid credentials

**Solution:**
1. **Check email:**
   - Make sure it's the email you use to log in to Jira
   - Some Jira instances need username instead
   - Try your full email (not shortened version)

2. **Check API token:**
   - Regenerate the token if needed
   - Make sure you copied the full token (it's long!)
   - Check for extra spaces before/after the token

3. **Check base URL:**
   - Must include `https://`
   - Must not end with `/`
   - Example: `https://company.atlassian.net` ✅
   - Example: `https://company.atlassian.net/` ❌

### "404 Project not found" Error

**Problem:** Wrong project key

**Solution:**
1. Check project key is correct
2. Make sure you have access to the project
3. Project key is case-sensitive (usually uppercase)
4. It's the part before the dash in issue keys (e.g., `PROJ-123` → key is `PROJ`)

### "403 Forbidden" Error

**Problem:** Insufficient permissions

**Solution:**
1. Make sure your account has permission to create issues in the project
2. Check project permissions in Jira
3. Contact Jira admin if needed

### "Issue type not found" Error

**Problem:** Wrong issue type name

**Solution:**
1. Check available issue types in your project:
   - Go to Project Settings → Issue types
   - Use exact name (case-sensitive)
   - Common types: `Task`, `Story`, `Bug`, `Epic`

2. Default is `Task` - change in query parameter:
   ```bash
   curl -X POST "http://localhost:8000/upload?jira_project_key=PROJ&jira_issue_type=Story" \
     -F "file=@meeting.mp3"
   ```

## Example .env File

```env
# Groq API (for action item extraction)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Jira Configuration
JIRA_BASE_URL=https://mycompany.atlassian.net
JIRA_EMAIL=john.doe@mycompany.com
JIRA_API_TOKEN=ATATT3xFfGF0abcdefghijklmnopqrstuvwxyz123456789

# Whisper (optional)
WHISPER_MODEL=base
USE_LOCAL_WHISPER=true

# File upload settings
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=100000000
```

## Using Different Projects

When uploading, specify the project key in the URL:

```bash
# For project "PROJ"
curl -X POST "http://localhost:8000/upload?jira_project_key=PROJ" -F "file=@audio.mp3"

# For project "DEV"
curl -X POST "http://localhost:8000/upload?jira_project_key=DEV" -F "file=@audio.mp3"
```

You can create issues in any project you have access to!

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Rotate API tokens** periodically
3. **Use project-specific tokens** if your Jira supports it
4. **Limit token permissions** if possible (though Jira API tokens usually have full access)

## Need Help?

- **Jira Admin Docs:** https://support.atlassian.com/jira-service-management-cloud/docs/manage-api-tokens-for-your-account/
- **Jira REST API:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Check server logs** for detailed error messages

