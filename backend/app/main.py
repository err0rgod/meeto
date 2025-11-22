"""
Simple Audio to Jira System
Extracts text from audio and creates Jira issues
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.config import settings
from app.services.jira_service import JiraService
import os
from pathlib import Path

# Initialize services
try:
    from app.services.whisper_service import whisper_service
except Exception as e:
    print(f"Warning: Whisper service not available: {e}")
    whisper_service = None

try:
    from app.services.llm_service import llm_service
except Exception as e:
    print(f"Warning: LLM service not available: {e}")
    llm_service = None

app = FastAPI(
    title="Audio to Jira",
    description="Extract text from audio and create Jira issues",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audio to Jira</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 16px;
                padding: 40px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            input[type="file"], input[type="text"], select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input[type="file"]:focus, input[type="text"]:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                border-radius: 8px;
                display: none;
            }
            .result.success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                display: block;
            }
            .result.error {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                display: block;
            }
            .result.loading {
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                display: block;
            }
            .issue-link {
                display: inline-block;
                margin-top: 10px;
                padding: 8px 16px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin-right: 10px;
            }
            .issue-link:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Audio to Jira</h1>
            <p class="subtitle">Upload audio or transcript and create Jira issues automatically</p>
            
            <form id="uploadForm">
                <div class="form-group">
                    <label for="audioFile">File (audio or transcript *.txt) *</label>
                    <input type="file" id="audioFile" name="file" accept=".mp3,.wav,.m4a,.ogg,.flac,.txt" required>
                </div>
                
                <div class="form-group">
                    <label for="projectKey">Jira Project Key *</label>
                    <input type="text" id="projectKey" name="jira_project_key" placeholder="e.g., PROJ" required>
                </div>
                
                <div class="form-group">
                    <label for="issueType">Issue Type</label>
                    <select id="issueType" name="jira_issue_type">
                        <option value="Task">Task</option>
                        <option value="Story">Story</option>
                        <option value="Bug">Bug</option>
                        <option value="Epic">Epic</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="priority">Priority</label>
                    <select id="priority" name="jira_priority">
                        <option value="Lowest">Lowest</option>
                        <option value="Low">Low</option>
                        <option value="Medium" selected>Medium</option>
                        <option value="High">High</option>
                        <option value="Highest">Highest</option>
                    </select>
                </div>
                
                <button type="submit" id="submitBtn">Upload & Create Jira Issue</button>
            </form>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            // Enhanced client: picks /upload or /upload-transcript automatically,
            // displays summary, action items, transcript preview, and Jira links.
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const resultDiv = document.getElementById('result');
                const submitBtn = document.getElementById('submitBtn');
                const fileInput = document.getElementById('audioFile');
                const file = fileInput.files[0];

                if (!file) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Please select a file to upload.';
                    return;
                }

                const fileName = file.name || '';
                const ext = fileName.split('.').pop().toLowerCase();
                const projectKey = document.getElementById('projectKey').value.trim();
                if (!projectKey) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Jira project key is required.';
                    return;
                }

                // Choose endpoint depending on file type
                let endpoint = '/upload';
                if (ext === 'txt') endpoint = '/upload-transcript';

                // Build FormData manually to support both endpoints
                const formData = new FormData();
                formData.append('file', file);
                formData.append('jira_project_key', projectKey);
                formData.append('jira_issue_type', document.getElementById('issueType').value);
                formData.append('jira_priority', document.getElementById('priority').value);

                // Show loading UI
                resultDiv.className = 'result loading';
                resultDiv.innerHTML = '⏳ Processing file and creating Jira issue(s)...';
                submitBtn.disabled = true;

                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json().catch(()=>({}));

                    if (!response.ok) {
                        const err = data.detail || data.error || 'Unknown error';
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${err}`;
                        return;
                    }

                    // Success — render structured results
                    resultDiv.className = 'result success';
                    let html = '<strong>✅ Success!</strong><br><br>';

                    if (data.summary) {
                        html += '<strong>Meeting Summary:</strong><br>';
                        html += `<pre style="white-space:pre-wrap; background:#f7f9fc; padding:10px; border-radius:6px;">${escapeHtml(data.summary)}</pre><br>`;
                    }

                    if (data.action_items && data.action_items.length > 0) {
                        html += '<strong>Action Items:</strong><br><ol>';
                        data.action_items.forEach(item => {
                            const desc = escapeHtml(item.description || item.summary || '');
                            const owner = item.owner ? ` — <em>${escapeHtml(item.owner)}</em>` : '';
                            html += `<li>${desc}${owner}</li>`;
                        });
                        html += '</ol>';
                    }

                    if (data.jira_issues && data.jira_issues.length > 0) {
                        html += '<strong>Jira Issues Created:</strong><br>';
                        data.jira_issues.forEach(issue => {
                            html += `<a href="${issue.url}" target="_blank" class="issue-link">${escapeHtml(issue.key)}</a>`;
                        });
                        html += '<br>';
                    }

                    if (data.transcript) {
                        const preview = escapeHtml(data.transcript.substring(0, 2000));
                        html += '<details><summary>Transcript (click to expand)</summary>';
                        html += `<pre style="white-space:pre-wrap; background:#fff; padding:10px; border-radius:6px;">${preview}</pre>`;
                        html += '</details>';
                    }

                    resultDiv.innerHTML = html;

                    // Reset form for convenience
                    document.getElementById('uploadForm').reset();

                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>❌ Error:</strong> ${escapeHtml(error.message || String(error))}`;
                } finally {
                    submitBtn.disabled = false;
                }
            });

            // Simple HTML escaping for inserted text
            function escapeHtml(str) {
                if (!str) return '';
                return String(str)
                    .replaceAll('&', '&amp;')
                    .replaceAll('<', '&lt;')
                    .replaceAll('>', '&gt;')
                    .replaceAll('"', '&quot;')
                    .replaceAll("'", '&#039;');
            }
        </script>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    jira_project_key: str = Form(...),
    jira_issue_type: str = Form("Task"),
    jira_priority: str = Form("Medium")
):
    """
    Upload audio file, extract text, and create Jira issue
    
    Form Parameters:
    - file: Audio file (required)
    - jira_project_key: Jira project key (required)
    - jira_issue_type: Issue type (optional, default: Task)
    - jira_priority: Priority (optional, default: Medium)
    """
    if not jira_project_key:
        raise HTTPException(
            status_code=400,
            detail="jira_project_key is required"
        )
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )

    # Handle text transcripts directly; for audio, save then transcribe
    file_path = None
    transcript_text = None

    if file_ext == ".txt":
        try:
            transcript_text = file_content.decode("utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Unable to decode text file. Please use UTF-8 encoded .txt files.")
    else:
        # Save file
        import uuid
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

    # At this point either `transcript_text` is set (for .txt uploads) or
    # an audio file was saved to `file_path` and needs transcription.
    try:
        if not transcript_text:
            if not whisper_service:
                raise HTTPException(
                    status_code=500,
                    detail="Whisper service not available. Set OPENAI_API_KEY in .env file"
                )

            transcript_result = whisper_service.transcribe(file_path)
            transcript_text = transcript_result["text"]

        # Delegate the rest of processing to helper
        result = await process_transcript_and_create_issues(
            transcript_text=transcript_text,
            filename=file.filename,
            jira_project_key=jira_project_key,
            jira_issue_type=jira_issue_type,
            jira_priority=jira_priority
        )

        # Clean up audio file if it was saved
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return result
    except HTTPException:
        # Re-raise HTTP exceptions, cleaning up saved file if any
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        # Clean up on error
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/upload-transcript")
async def upload_transcript(
    file: UploadFile = File(...),
    jira_project_key: str = Form(...),
    jira_issue_type: str = Form("Task"),
    jira_priority: str = Form("Medium")
):
    """
    Upload a plain text transcript (.txt) and create Jira issues.
    """
    if not jira_project_key:
        raise HTTPException(status_code=400, detail="jira_project_key is required")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext != ".txt":
        raise HTTPException(status_code=400, detail="Only .txt transcript files are accepted by this endpoint")

    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB")

    try:
        transcript_text = file_content.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to decode text file. Please use UTF-8 encoded .txt files.")

    try:
        result = await process_transcript_and_create_issues(
            transcript_text=transcript_text,
            filename=file.filename,
            jira_project_key=jira_project_key,
            jira_issue_type=jira_issue_type,
            jira_priority=jira_priority
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing transcript: {e}")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def process_transcript_and_create_issues(
    transcript_text: str,
    filename: str,
    jira_project_key: str,
    jira_issue_type: str,
    jira_priority: str
) -> dict:
    """
    Helper to extract action items, summarize, and create Jira issues from a transcript.
    Returns the same response payload used by the endpoints.
    """
    # Extract action items and generate summary
    action_items = []
    summary = None

    if llm_service:
        try:
            llm_result = llm_service.extract_action_items(transcript_text)
            action_items = llm_result.get("tasks", [])
        except Exception as e:
            print(f"LLM extraction failed: {e}")

        try:
            summary = llm_service.summarize_transcript(transcript_text)
        except Exception as e:
            print(f"LLM summarization failed: {e}")
            summary = None

    # Create Jira service and validate project key early
    if not all([settings.JIRA_BASE_URL, settings.JIRA_EMAIL, settings.JIRA_API_TOKEN]):
        raise HTTPException(
            status_code=500,
            detail="Jira credentials not configured. Check JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in .env"
        )

    jira_service = JiraService(
        base_url=settings.JIRA_BASE_URL,
        email=settings.JIRA_EMAIL,
        api_token=settings.JIRA_API_TOKEN
    )

    # Validate project key exists and is accessible
    try:
        jira_service.get_project(jira_project_key)
    except RuntimeError as e:
        # Jira returned a helpful body; surface it to client
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or inaccessible project key: {e}")

    # Create Jira issue(s)
    created_issues = []

    if action_items:
        # Create one issue per action item
        for item in action_items:
            priority_map = {
                "low": "Lowest",
                "medium": "Medium",
                "high": "High",
                "critical": "Highest"
            }

            assignee_id = None
            owner_val = item.get("owner")
            if owner_val:
                try:
                    assignee_id = jira_service.find_user(owner_val, project_key=jira_project_key)
                except Exception as e:
                    # If lookup fails, log and continue without assignee
                    print(f"Jira user lookup failed for '{owner_val}': {e}")

            issue = jira_service.create_issue(
                summary=item.get("description", "No description")[:255],
                description=f"**Extracted from transcript**\n\n{item.get('description')}\n\n**Full Transcript:**\n{transcript_text[:5000]}",
                project_key=jira_project_key,
                issue_type=jira_issue_type,
                priority=priority_map.get(item.get("priority", "medium"), "Medium"),
                due_date=item.get("deadline"),
                assignee=assignee_id
            )
            created_issues.append(issue)
    else:
        # Create single issue with summary + full transcript
        desc = ""
        if summary:
            desc += f"**Meeting Summary:**\n\n{summary}\n\n"
        desc += f"**Full Transcript**\n\n{transcript_text}"

        issue = jira_service.create_issue(
            summary=f"Transcript: {filename}",
            description=desc,
            project_key=jira_project_key,
            issue_type=jira_issue_type,
            priority=jira_priority
        )
        created_issues.append(issue)

    return {
        "success": True,
        "transcript": transcript_text,
        "summary": summary,
        "action_items": action_items,
        "jira_issues": [
            {
                "key": issue["key"],
                "url": f"{settings.JIRA_BASE_URL}/browse/{issue['key']}"
            }
            for issue in created_issues
        ]
    }
