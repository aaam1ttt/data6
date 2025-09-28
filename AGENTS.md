# AGENTS.md

## Commands

### Setup
```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install flask qrcode pillow openpyxl werkzeug
```

### Dev Server
```bash
cd qr-data-main/project_root
python run.py
```

### Running Tests
No test framework configured.

## Tech Stack
- **Backend**: Flask with SQLite
- **QR Codes**: qrcode, PIL/Pillow
- **Forms**: Custom parser for ТОРГ-12, Excel processing with openpyxl
- **Auth**: Flask sessions with werkzeug password hashing

## Architecture
- MVC structure: routes/, models/, templates/
- Data stored in app/data/ (SQLite), storage/ (files)
- Blueprints: main, auth, admin, forms, scan
- Core modules: codes.py (QR/barcode gen), forms_parser.py

## Code Style
- Russian comments and UI text
- Type hints with typing module
- Snake_case naming convention
