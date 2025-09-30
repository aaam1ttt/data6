# AGENTS.md

## Commands

### Initial Setup
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install flask pillow qrcode[pil] openpyxl werkzeug pylibdmtx-windows opencv-python pdf417gen barcode python-python-barcode pyzbar pdf417decoder pyzxing reportlab python-dateutil pylibdmtx python-barcode pdf417gen numpy aztec-code-generator
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

### Test Aztec Generation
```bash
python test_aztec_full_workflow.py
```

## Tech Stack & Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with custom extensions
- **QR/Barcode generation**: qrcode, pylibdmtx, python-barcode, pdf417gen, aztec-code-generator
- **Barcode scanning**: pyzbar, pylibdmtx, pyzxing (ZXing Java library for Aztec)
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

## Aztec Code Implementation
Aztec code generation is now fully functional using:
1. **Primary**: aztec-code-generator (pure Python) - generates valid Aztec codes
2. **Fallback 1**: treepoem (requires Ghostscript) 
3. **Fallback 2**: Custom numpy-based implementation

Aztec codes are scannable via:
- pyzxing (ZXing Java library) - best for Aztec
- pyzbar (supports Aztec)
- Other ZXing-based scanners

Key implementation details:
- aztec-code-generator uses latin-1 encoding (UTF-8 chars fall back to other methods)
- Matrix conversion: 0=white, 1=black in source, inverted for display
- High-resolution scaling with NEAREST resampling for crisp modules
- Proper quiet zone (border) added per Aztec spec
- Integration with decode_auto() for scanning validation
