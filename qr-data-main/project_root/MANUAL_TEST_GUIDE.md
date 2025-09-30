# Manual Testing Guide - Excel Save Dialog

## Quick Test Steps

### Prerequisites
1. Start the development server:
   ```bash
   cd qr-data-main\project_root
   python run.py
   ```
2. Open browser: http://127.0.0.1:5000

### Test Scenario 1: Basic Excel Export with Save Dialog

1. **Navigate to Scan Page**
   - Go to http://127.0.0.1:5000/scan

2. **Upload or Scan a QR Code with Table Data**
   - Option A: Use the camera to scan a QR code
   - Option B: Upload an image file
   - Option C: Paste from clipboard (Ctrl+V)
   - The QR code should contain data that corresponds to one of these forms:
     - TORG-12 (prefix: T12_)
     - Message (prefix: MSG_)
     - Exploitation (prefix: EXP_)
     - Transport (prefix: TRN_)
     - Custom table

3. **Verify Button Appearance**
   - After successful scan, verify that:
     - "Сохранить в Excel" button appears
     - Button is visible and enabled

4. **Click "Сохранить в Excel" Button**
   - Click the button
   - **Expected Result** (Modern browsers: Chrome 86+, Edge 86+, Firefox 111+):
     - Native OS file save dialog appears
     - Default filename is suggested (e.g., "torg12.xlsx")
     - File type filter shows "Excel файлы (*.xlsx)"
     - You can navigate to choose destination folder
     - You can modify the filename

   - **Expected Result** (Older browsers: Safari, older Firefox):
     - File downloads to default Downloads folder
     - No dialog appears (standard download behavior)

5. **Choose Location and Save**
   - Select a destination folder
   - Optionally modify the filename
   - Click "Save" in the dialog
   - **Expected Result**:
     - Success message appears: "Файл успешно сохранен"
     - File is saved to chosen location
     - You can open the file in Excel/LibreOffice

6. **Verify Excel File Contents**
   - Open the saved .xlsx file
   - Verify it contains the expected data structure
   - For TORG-12: Columns should be "Код", "Наименование", "Значение"
   - Data should match what was in the QR code

### Test Scenario 2: Cancel Dialog

1. Repeat steps 1-4 from Scenario 1
2. When save dialog appears, click "Cancel"
3. **Expected Result**:
   - No error message appears
   - No file is saved
   - UI remains functional

### Test Scenario 3: Different Form Types

Test each form type to verify correct default filenames:

| Form Type | Expected Default Filename |
|-----------|---------------------------|
| TORG-12 | torg12.xlsx |
| Message | message.xlsx |
| Exploitation | exploitation.xlsx |
| Transport | transport.xlsx |
| Custom | custom.xlsx |

### Test Scenario 4: Error Handling

1. **Test without network** (optional):
   - Disable network
   - Try to export
   - Should show: "Ошибка сети при сканировании"

2. **Test with modified data** (optional):
   - Use browser dev tools
   - Modify currentExcelData to invalid values
   - Should show appropriate error message

## Browser Compatibility Check

Test on multiple browsers:

| Browser | Expected Behavior |
|---------|-------------------|
| Chrome 100+ | ✅ Native save dialog |
| Edge 100+ | ✅ Native save dialog |
| Firefox 111+ | ✅ Native save dialog |
| Safari | ⚠️ Standard download (no dialog) |
| Firefox < 111 | ⚠️ Standard download (no dialog) |

## Visual Verification

Screenshots to check:
1. Button label says "Сохранить в Excel" (not "Открыть в Excel")
2. Native file save dialog appears (modern browsers)
3. File type filter shows "Excel файлы"
4. Default filename is appropriate for form type
5. Success message after save

## Common Issues and Solutions

### Issue: Button doesn't appear
- **Cause**: QR code doesn't contain table data
- **Solution**: Ensure QR code has recognized prefix (T12_, MSG_, etc.)

### Issue: Dialog doesn't appear
- **Cause**: Browser doesn't support File System Access API
- **Solution**: Expected behavior - file downloads normally

### Issue: File is corrupt
- **Cause**: Backend error generating Excel
- **Solution**: Check browser console and server logs

### Issue: Error message appears
- **Check**: Browser console for JavaScript errors
- **Check**: Network tab for API response
- **Check**: Server logs for Python errors

## Success Criteria

✅ Button appears after scanning table-form QR codes
✅ Button label is "Сохранить в Excel"
✅ Native save dialog appears (modern browsers)
✅ Default filename matches form type
✅ File type filter works correctly
✅ Can choose destination folder
✅ Can modify filename before saving
✅ File saves to chosen location
✅ Success message appears
✅ Excel file opens correctly
✅ Data in Excel matches scanned data
✅ Fallback download works (older browsers)
✅ Cancel dialog works without errors

## Additional Notes

- File System Access API requires HTTPS in production (localhost is exempt)
- User must grant permission for each save operation
- Permission is per-session (not persistent)
- Some browsers may show additional security prompts
