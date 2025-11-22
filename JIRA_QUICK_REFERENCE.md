# Jira Quick Reference

## Required Information

To use Jira integration, you need **3 things**:

1. **Jira Base URL**
   - Example: `https://yourcompany.atlassian.net`
   - Find it in your browser when you visit Jira

2. **Your Jira Email**
   - The email you use to log in to Jira
   - Example: `john.doe@company.com`

3. **Jira API Token**
   - Create at: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy immediately (shown only once!)

## .env Configuration

```env
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=ATATT3xFfGF0...your-token
```

## Usage

When uploading audio, specify the project key:

```bash
curl -X POST "http://localhost:8000/upload?jira_project_key=PROJ" \
  -F "file=@meeting.mp3"
```

**Project Key:**
- Found in issue keys like `PROJ-123`
- The part before the dash (`PROJ`)
- Usually 2-10 uppercase letters

## Common Errors

| Error | Solution |
|-------|----------|
| "Jira credentials not configured" | Check all 3 values in `.env` |
| "401 Unauthorized" | Check email and API token are correct |
| "404 Project not found" | Check project key is correct |
| "403 Forbidden" | Check you have permission to create issues |

## Need More Help?

See `SETUP_JIRA.md` for detailed step-by-step guide with screenshots and troubleshooting.

