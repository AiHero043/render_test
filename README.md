# EROME Automation - Frontend (Web UI)

## Overview
Web-based configuration interface for managing automation profiles and viewing job status.

## Files
- `web_ui.py` - Flask web server
- `database.py` - SQLite database manager
- `templates/index.html` - Web interface

## Installation

```bash
cd frontend
pip install -r requirements.txt
```

## Usage

### Start Frontend Server:
```bash
python web_ui.py
```

Access at: http://localhost:5001

### Configuration:
- **Port**: 5001 (change in web_ui.py)
- **Database**: ../profiles.db (shared with backend)

## Features
- Create/Edit/Delete profiles
- Queue automation jobs
- View job status and history
- Reset automation state
- View logs

## API Endpoints

### Profiles
- `GET /api/profiles` - List all profiles
- `GET /api/profiles/<id>` - Get profile
- `POST /api/profiles` - Create profile
- `PUT /api/profiles/<id>` - Update profile
- `DELETE /api/profiles/<id>` - Delete profile

### Jobs
- `POST /api/profiles/<id>/run` - Create job (queue for worker)
- `GET /api/jobs/<id>` - Get job status
- `GET /api/profiles/<id>/jobs` - List profile jobs

### State
- `POST /api/profiles/<id>/reset-state` - Reset automation state

## Deployment

### Development:
```bash
python web_ui.py
```

### Production with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 web_ui:app
```

### With Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Schema

### profiles table
- Profile configurations

### automation_states table
- Per-profile automation state

### jobs table
- Job queue with status tracking
- Statuses: pending, running, completed, failed
