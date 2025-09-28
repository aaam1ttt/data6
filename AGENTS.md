# AGENTS.md

## Commands

### Initial Setup
```bash
# Create and activate virtual environment (project uses standard .venv location)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install flask werkzeug pillow qrcode[pil]
```

### Running Dev Server
```bash
cd qr-data-main/project_root
python run.py
```

### Running Tests
No test framework configured.

## Tech Stack & Architecture

**Backend**: Flask (Python) with SQLite database  
**Frontend**: HTML templates with Jinja2  
**Features**: QR code generation, user authentication, file uploads, form processing

**Structure**: 
- `app/` - Main Flask application
- `app/routes/` - Route handlers (main, auth, admin, forms, scan)
- `app/models/` - Database models (users, history)  
- `app/core/` - Core utilities (QR codes, forms parser)
- `app/static/` - Static assets
- `app/templates/` - Jinja2 templates