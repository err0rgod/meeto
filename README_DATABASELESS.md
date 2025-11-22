# Automated Meeting Secretary - Database-less Version

**No database required!** This version uses file-based JSON storage instead of a database.

## What Changed?

- ✅ **No database setup needed** - No PostgreSQL, MySQL, or Supabase required
- ✅ **File-based storage** - All data stored in JSON files in `./storage/` directory
- ✅ **Simpler setup** - Just install Python dependencies and run
- ✅ **Same API** - All endpoints work exactly the same
- ✅ **Easy backup** - Just copy the `storage/` folder

## Quick Start

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
# Security
SECRET_KEY=your-secret-key-change-in-production

# Groq API (for LLM extraction)
GROQ_API_KEY=your-groq-api-key

# Storage (optional - defaults to ./storage)
STORAGE_DIR=./storage

# Other settings...
```

### 3. Run the Server

```bash
python run.py
```

That's it! No database setup needed! 🎉

## Storage Structure

Data is stored in JSON files in the `storage/` directory:

```
storage/
├── users.json          # User accounts
├── meetings.json       # Meeting records
├── tasks.json          # Extracted tasks
└── integrations.json   # Jira/Trello integrations
```

## Backup & Restore

**Backup:**
```bash
# Just copy the storage folder
cp -r storage storage_backup
```

**Restore:**
```bash
# Replace storage folder
rm -rf storage
cp -r storage_backup storage
```

## Migration from Database Version

If you had data in a database:

1. Export data as JSON (if possible)
2. Import into storage files manually
3. Or start fresh - storage files will be created automatically

## Limitations

- **Not for production scale** - File-based storage doesn't scale well
- **No concurrent writes** - Multiple processes writing can cause issues
- **No transactions** - No rollback capability
- **File locking** - Simple implementation, may have race conditions

**For production**, consider:
- Using a proper database (PostgreSQL, MySQL)
- Or upgrading to a database-backed version

## Benefits

- ✅ **Zero setup** - No database installation
- ✅ **Portable** - Easy to move/copy
- ✅ **Simple** - Easy to understand and debug
- ✅ **Fast development** - No database migrations
- ✅ **Easy testing** - Just delete storage folder

## File Format

Each storage file is a JSON array:

```json
[
  {
    "id": "uuid-here",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00",
    ...
  }
]
```

## Troubleshooting

### Storage files not created?

- Check write permissions in the project directory
- Ensure `storage/` directory can be created

### Data lost?

- Check `storage/` folder exists
- Verify JSON files are valid JSON
- Check file permissions

### Concurrent access issues?

- Only run one instance of the server
- For multiple instances, use a database version

