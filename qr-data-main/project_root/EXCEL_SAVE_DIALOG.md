# Excel Save Dialog Implementation

## Overview

The "Open in Excel" button (renamed to "Сохранить в Excel") now triggers a file save dialog that prompts users to choose a destination folder and specify a filename before saving the Excel file.

## Changes Made

### 1. Backend Changes (`app/routes/scan.py`)

#### Modified `export_excel()` Endpoint
- **Before**: Returned redirect/flash messages for errors
- **After**: Returns JSON error responses for better AJAX handling
- **Behavior**: Still returns Excel file as `send_file()` with proper MIME type and headers

```python
# Error handling now returns JSON
return jsonify({"ok": False, "error": "Нет табличной формы для экспорта"}), 400

# Success still returns file
return send_file(bio, as_attachment=True, download_name=filename,
                 mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
```

### 2. Frontend Changes (`app/templates/scan.html`)

#### Button Label Update
- **Before**: "Открыть в Excel"
- **After**: "Сохранить в Excel"

#### Removed Form Submission
- Removed hidden form (`excelForm`) that was used for POST submission
- Removed hidden inputs (`excelText`, `excelFormType`)

#### New JavaScript Implementation

##### Data Storage
```javascript
let currentExcelData = {text: '', form_type: ''};
```
Stores the current scan data for Excel export.

##### Save Dialog Handler
Uses modern File System Access API (`showSaveFilePicker`) for native save dialogs:

```javascript
openExcelBtn.addEventListener('click', async () => {
    // 1. Fetch Excel file from backend via AJAX
    const response = await fetch('/scan/export_excel', {
        method: 'POST',
        body: formData
    });
    
    // 2. Show native save dialog (if supported)
    const handle = await window.showSaveFilePicker({
        suggestedName: defaultFilename,
        types: [{
            description: 'Excel файлы',
            accept: {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']}
        }]
    });
    
    // 3. Write file to chosen location
    const writable = await handle.createWritable();
    await writable.write(blob);
    await writable.close();
});
```

##### Helper Functions

**`getDefaultFilename(formType)`**
- Returns appropriate filename based on form type
- Maps: torg12 → torg12.xlsx, message → message.xlsx, etc.

**`fallbackDownload(blob, filename)`**
- Provides backward compatibility for browsers without File System Access API
- Creates temporary download link and triggers download

## User Experience

### Modern Browsers (Chrome 86+, Edge 86+)
1. User scans QR/barcode with table data
2. Clicks "Сохранить в Excel" button
3. Native OS file save dialog appears
4. User can:
   - Choose destination folder
   - Modify filename (default: `torg12.xlsx`, `message.xlsx`, etc.)
   - See file type filter (Excel files .xlsx)
5. File is saved to chosen location
6. Success message displayed

### Older Browsers (Safari, Firefox < 111)
1. Same initial steps
2. Standard browser download behavior (file saved to default Downloads folder)
3. User can still rename/move after download

## Error Handling

### Backend Validation
- Missing or empty text → 400 error
- Invalid form_type → 400 error
- Returns JSON: `{"ok": false, "error": "..."}`

### Frontend Handling
- Network errors → Shows error alert
- User cancels save dialog → No error (AbortError ignored)
- File System API unavailable → Automatic fallback to standard download

## File Type Configuration

```javascript
types: [{
    description: 'Excel файлы',
    accept: {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    }
}]
```

This ensures:
- File picker only shows/accepts .xlsx files
- Proper MIME type association
- Clear user experience

## Browser Compatibility

| Browser | Save Dialog | Behavior |
|---------|-------------|----------|
| Chrome 86+ | ✅ Native | Full file picker dialog |
| Edge 86+ | ✅ Native | Full file picker dialog |
| Firefox 111+ | ✅ Native | Full file picker dialog |
| Safari | ❌ Fallback | Standard download |
| Firefox < 111 | ❌ Fallback | Standard download |

## Testing

Run the test suite to verify functionality:

```bash
python test_excel_save_functionality.py
```

Tests include:
- ✅ Backend generates valid Excel files
- ✅ Proper MIME types and headers
- ✅ Default filenames for each form type
- ✅ Error handling (invalid inputs)
- ✅ Frontend JavaScript integration
- ✅ Save dialog API usage
- ✅ Fallback download support

## Default Filenames

| Form Type | Default Filename |
|-----------|------------------|
| torg12 | torg12.xlsx |
| message | message.xlsx |
| exploitation | exploitation.xlsx |
| transport | transport.xlsx |
| custom | custom.xlsx |

## Security Considerations

- User must explicitly grant permission to save file (browser security)
- No automatic file writes without user interaction
- File type is validated on both frontend and backend
- Maximum file size limits still apply (20 MB)

## Future Enhancements

Potential improvements:
- Add timestamp to default filename
- Remember last save location (with permission)
- Batch export multiple scans
- Custom filename templates
- Export to other formats (CSV, JSON)
