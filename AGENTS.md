# AGENTS.md

## Commands

### Initial Setup
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install flask pillow qrcode[pil] openpyxl werkzeug pylibdmtx-windows opencv-python pdf417gen barcode python-python-barcode pyzbar pdf417decoder pyzxing reportlab python-dateutil pylibdmtx python-barcode pdf417gen numpy
```

### Build
```bash
cd qr-data-main\project_root
python -c "from app import create_app; app = create_app(); print('Build successful')"
```

### Run Dev Server
```bash
cd qr-data-main\project_root
python run.py
```

### Admin Setup
```bash
python create_admin.py
```

### Diagnostics
```bash
python diagnose_login.py
```

## Tech Stack & Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with custom extensions
- **QR/Barcode generation**: qrcode, pylibdmtx, python-barcode, pdf417gen
- **Image processing**: PIL, OpenCV, numpy
- **File formats**: openpyxl, reportlab
- **Architecture**: Blueprint-based routes, SQLite with manual schema management
- **Structure**: `app/` (main app), `models/` (data), `routes/` (endpoints), `core/` (business logic), `templates/` (HTML), `static/` (assets)
- File storage for generated codes and uploads in `app/storage/`

## Code Style
- Russian comments/strings, English code
- Snake_case for variables/functions
- Blueprint registration pattern
- Manual database connection management via Flask g
- Type hints where applicable
