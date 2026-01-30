"""
Meeto SaaS Backend
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
import json
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.database import engine, get_db, Base
from app.models import Meeting, ActionItem
from app.services.jira_service import JiraService

# Initialize services
try:
    from app.services.assemblyai_service import assemblyai_service
    # Alias for backward compatibility in logic
    transcription_service = assemblyai_service
except Exception as e:
    print(f"Warning: AssemblyAI service not available: {e}")
    transcription_service = None

try:
    from app.services.llm_service import llm_service
except Exception as e:
    print(f"Warning: LLM service not available: {e}")
    llm_service = None

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meeto SaaS",
    description="Meeting Recorder & Jira Integrator",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# --- Background Tasks ---
def process_meeting_background(meeting_id: int, db: Session):
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return

        print(f"Processing meeting {meeting_id}...")

        # 1. Transcribe (AssemblyAI)
        if not transcription_service:
            print("Transcription service missing")
            meeting.status = "ERROR"
            db.commit()
            return

        try:
            transcript_result = transcription_service.transcribe(meeting.audio_path)
            meeting.transcript_text = transcript_result["text"]
            db.commit()
        except Exception as e:
            print(f"Transcription failed: {e}")
            meeting.status = "ERROR"
            db.commit()
            return

        # 2. Extract Action Items & Summary
        if llm_service:
            try:
                llm_result = llm_service.extract_action_items(meeting.transcript_text)
                action_items_data = llm_result.get("tasks", [])
                
                # Save Action Items
                for item in action_items_data:
                    action_item = ActionItem(
                        meeting_id=meeting.id,
                        description=item.get("description"),
                        owner=item.get("owner"),
                        priority=item.get("priority", "Medium")
                    )
                    db.add(action_item)
                
                # Summary
                meeting.summary_text = llm_service.summarize_transcript(meeting.transcript_text)
                
            except Exception as e:
                print(f"LLM processing failed: {e}")

        meeting.status = "COMPLETED"
        db.commit()
        print(f"Meeting {meeting_id} processing complete.")

    except Exception as e:
        print(f"Error processing meeting {meeting_id}: {e}")
        # Re-query in case session detached
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "ERROR"
            db.commit()

# --- API Endpoints ---

@app.post("/api/upload-stream")
async def upload_stream(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """endpoint for Chrome Extension to upload audio blob"""
    
    # Save file
    file_ext = ".webm" # Extension usually sends webm
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create Meeting record
    new_meeting = Meeting(
        title=f"Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        audio_path=file_path,
        status="PROCESSING"
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    # Trigger background processing
    background_tasks.add_task(process_meeting_background, new_meeting.id, db)

    return {"success": True, "meeting_id": new_meeting.id}

@app.get("/api/meetings")
def list_meetings(db: Session = Depends(get_db)):
    meetings = db.query(Meeting).order_by(Meeting.timestamp.desc()).all()
    if not meetings:
        return []
    return meetings

@app.get("/api/meetings/{meeting_id}")
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Include action items
    return {
        "id": meeting.id,
        "title": meeting.title,
        "timestamp": meeting.timestamp,
        "status": meeting.status,
        "transcript": meeting.transcript_text,
        "summary": meeting.summary_text,
        "action_items": meeting.action_items
    }

@app.post("/api/meetings/{meeting_id}/sync-jira")
def sync_jira(
    meeting_id: int,
    project_key: str = Form(...),
    db: Session = Depends(get_db)
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not meeting.action_items:
        return {"success": False, "message": "No action items to sync"}

    # Initialize Jira
    if not all([settings.JIRA_BASE_URL, settings.JIRA_EMAIL, settings.JIRA_API_TOKEN]):
        raise HTTPException(status_code=500, detail="Jira credentials missing")

    jira_service = JiraService(
        base_url=settings.JIRA_BASE_URL,
        email=settings.JIRA_EMAIL,
        api_token=settings.JIRA_API_TOKEN
    )

    created_ct = 0
    for item in meeting.action_items:
        if item.jira_ticket_key:
            continue # Already synced

        try:
            # Simple sync
            issue = jira_service.create_issue(
                summary=item.description[:255],
                description=f"From Meeting: {meeting.title}\n\nOwner: {item.owner}\n\n{item.description}",
                project_key=project_key,
                issue_type="Task",
                priority=item.priority or "Medium"
            )
            item.jira_ticket_key = issue['key']
            item.jira_ticket_url = f"{settings.JIRA_BASE_URL}/browse/{issue['key']}"
            created_ct += 1
        except Exception as e:
            print(f"Failed to sync item {item.id}: {e}")

    db.commit()
    return {"success": True, "synced_count": created_ct}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    # Simple Dashboard to view meetings
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meeto Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; padding: 20px; }
            .meeting-card { cursor: pointer; transition: 0.2s; }
            .meeting-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Meeto Dashboard</h1>
            <div class="row">
                <div class="col-md-4">
                    <h3>Recent Meetings</h3>
                    <div id="meetingList" class="list-group">
                        <!-- Meetings inserted here -->
                        <div class="text-center p-3 text-muted">Loading...</div>
                    </div>
                    <div class="mt-3 text-center">
                        <button class="btn btn-sm btn-outline-secondary" onclick="loadMeetings()">Refresh List</button>
                    </div>
                </div>
                <div class="col-md-8">
                    <div id="meetingDetail" class="card p-4 d-none">
                        <h2 id="mTitle"></h2>
                        <span id="mStatus" class="badge bg-secondary mb-3"></span>
                        
                        <h5>Summary</h5>
                        <p id="mSummary" class="text-muted">No summary yet...</p>

                        <h5>Action Items</h5>
                        <ul id="mActionItems" class="list-group mb-4"></ul>

                        <h5>Transcript</h5>
                        <div style="max-height: 200px; overflow-y: auto; background: #eee; padding: 10px; border-radius: 5px;">
                            <pre id="mTranscript" style="white-space: pre-wrap; font-size: 0.8em;"></pre>
                        </div>
                        
                        <hr>
                        <div class="mt-3">
                            <label>Sync to Jira Project:</label>
                            <div class="input-group">
                                <input type="text" id="jiraProject" class="form-control" placeholder="Key (e.g. PROJ)">
                                <button class="btn btn-primary" onclick="syncJira()">Sync Issues</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentMeetingId = null;

            async function loadMeetings() {
                try {
                    const res = await fetch('/api/meetings');
                    const meetings = await res.json();
                    const list = document.getElementById('meetingList');
                    list.innerHTML = '';
                    
                    if (meetings.length === 0) {
                        list.innerHTML = '<div class="list-group-item">No meetings found.</div>';
                        return;
                    }

                    meetings.forEach(m => {
                        const item = document.createElement('a');
                        item.className = 'list-group-item list-group-item-action meeting-card';
                        item.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">${m.title}</h5>
                                <small>${new Date(m.timestamp).toLocaleDateString()}</small>
                            </div>
                            <p class="mb-1">Status: ${m.status}</p>
                        `;
                        item.onclick = () => loadDetail(m.id);
                        list.appendChild(item);
                    });
                } catch (e) {
                    console.error("Failed to load meetings", e);
                }
            }

            async function loadDetail(id) {
                currentMeetingId = id;
                document.getElementById('meetingDetail').classList.remove('d-none');
                
                const res = await fetch(`/api/meetings/${id}`);
                const m = await res.json();

                document.getElementById('mTitle').innerText = m.title;
                document.getElementById('mStatus').innerText = m.status;
                document.getElementById('mSummary').innerText = m.summary || "Pending...";
                document.getElementById('mTranscript').innerText = m.transcript || "Pending...";

                const ul = document.getElementById('mActionItems');
                ul.innerHTML = '';
                if (m.action_items && m.action_items.length > 0) {
                    m.action_items.forEach(ai => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item d-flex justify-content-between align-items-center';
                        
                        let jiraBadge = '';
                        if (ai.jira_ticket_key) {
                            jiraBadge = `<a href="${ai.jira_ticket_url}" target="_blank" class="badge bg-success ms-2">${ai.jira_ticket_key}</a>`;
                        }

                        li.innerHTML = `
                            <div>
                                <strong>${ai.description}</strong><br>
                                <small class="text-muted">Owner: ${ai.owner || 'Unassigned'} | Priority: ${ai.priority}</small>
                            </div>
                            ${jiraBadge}
                        `;
                        ul.appendChild(li);
                    });
                } else {
                    ul.innerHTML = '<li class="list-group-item">No action items found.</li>';
                }
            }

            async function syncJira() {
                if (!currentMeetingId) return;
                const projectKey = document.getElementById('jiraProject').value.trim();
                if (!projectKey) return alert("Enter Project Key");

                const formData = new FormData();
                formData.append('project_key', projectKey);

                try {
                    const res = await fetch(`/api/meetings/${currentMeetingId}/sync-jira`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert(`Synced ${data.synced_count} issues!`);
                        loadDetail(currentMeetingId); // Refresh
                    } else {
                        alert("Sync failed: " + (data.message || data.detail));
                    }
                } catch (e) {
                    alert("Error: " + e);
                }
            }

            loadMeetings();
            // Refresh every 30s to check processing status
            setInterval(loadMeetings, 30000);
        </script>
    </body>
    </html>
    """
