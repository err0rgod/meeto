"""
Simple test script to upload audio and create Jira issue
"""
import requests
import sys

def upload_audio(file_path, jira_project_key, base_url="http://localhost:8000"):
    """Upload audio file and create Jira issue"""
    
    url = f"{base_url}/upload"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        params = {
            "jira_project_key": jira_project_key,
            "jira_issue_type": "Task",
            "jira_priority": "Medium"
        }
        
        print(f"Uploading {file_path}...")
        response = requests.post(url, files=files, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success!")
            print(f"\nTranscript: {result['transcript'][:200]}...")
            print(f"\nAction Items Found: {len(result.get('action_items', []))}")
            print(f"\nJira Issues Created:")
            for issue in result.get('jira_issues', []):
                print(f"  - {issue['key']}: {issue['url']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_upload.py <audio_file> <jira_project_key>")
        print("Example: python test_upload.py meeting.mp3 PROJ")
        sys.exit(1)
    
    upload_audio(sys.argv[1], sys.argv[2])

