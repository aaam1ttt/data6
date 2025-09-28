# QR Data Flask Application

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install flask pillow qrcode[pil] openpyxl werkzeug pylibdmtx-windows opencv-python pdf417gen barcode python-python-barcode pyzbar pdf417decoder pyzxing reportlab python-dateutil
python create_admin.py
```

## Commands
- **Dev server**: `python run.py`
- **Create admin**: `python create_admin.py`
- **Diagnose login**: `python diagnose_login.py`

## Tech Stack
- **Backend**: Flask, SQLite
- **QR/Barcode**: qrcode, pylibdmtx, pyzbar, pdf417gen
- **Image processing**: PIL, OpenCV, NumPy
- **File formats**: openpyxl, reportlab

## Architecture
- Flask blueprints for routing (`auth`, `admin`, `forms`, `scan`)
- SQLite database with user authentication and history tracking
- File storage for generated codes and uploads in `app/storage/`
- Template-based UI with Jinja2
