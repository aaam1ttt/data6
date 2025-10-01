# Scan State Preservation Test Plan

## Implementation Summary

The scan window now preserves the scanned code and preview when navigating back from forms opened via "открыть форму" button, while clearing state when switching tabs through the top menu.

## Modified Files

### 1. app/templates/scan.html
- Added state tracking constants: `SCAN_STATE_KEY` and `FROM_FORM_KEY`
- Added `saveScanState()` - saves preview image, text, code type, button states, and Excel data to sessionStorage
- Added `restoreScanState()` - restores all saved state on page load
- Added `clearScanState()` - clears saved state from sessionStorage
- Modified `resetUI()` to clear state when doing full reset
- Modified `startScan()` to call `saveScanState()` after successful scan
- Added event listener on `openFormBtn` to mark navigation as from form
- Added DOMContentLoaded listener to restore state if returning from form
- Added event listeners on top menu links to clear state when navigating away from scan page

### 2. app/templates/form_torg12.html
- Added id="backBtn" to back button
- Added event listener to back button when from_scan=1 to set fromFormNavigation flag

### 3. app/templates/form_message.html
- Added id="backBtn" to back button
- Added event listener to back button when from_scan=1 to set fromFormNavigation flag

### 4. app/templates/form_exploitation.html
- Added id="backBtn" to back button
- Added event listener to back button when from_scan=1 to set fromFormNavigation flag

### 5. app/templates/form_transport.html
- Added id="backBtn" to back button
- Added event listener to back button when from_scan=1 to set fromFormNavigation flag

### 6. app/templates/form_custom.html
- Added id="backBtn" to back button
- Added event listener to back button when from_scan=1 to set fromFormNavigation flag

## How It Works

### State Preservation Flow

1. **User scans code**: After successful scan, `saveScanState()` is called automatically
   - Saves to sessionStorage: preview image src, recognized text, code type, file info, button visibility, Excel data

2. **User clicks "Открыть форму"**: 
   - Sets sessionStorage flag `fromFormNavigation = 'true'`
   - Navigates to form page with `from_scan=1` parameter

3. **User clicks "← Назад" in form**:
   - Back button has event listener that sets `fromFormNavigation = 'true'` again
   - Navigates back to scan page

4. **Scan page loads**:
   - DOMContentLoaded event checks for `fromFormNavigation` flag
   - If flag exists, calls `restoreScanState()` to restore all scan results
   - Removes the flag to prevent repeated restoration

5. **User clicks top menu tab** (Главная, Создать код, История, etc.):
   - Event listener intercepts navigation
   - Calls `clearScanState()` to remove saved state
   - Navigation proceeds normally

### State Clearing Flow

1. **User clicks "Очистить" button**: 
   - Calls `resetUI(true)` which includes `clearScanState()`

2. **User navigates via top menu**:
   - Event listeners on menu links detect navigation away from scan page
   - Calls `clearScanState()` before navigation

3. **User starts new scan**:
   - State is overwritten by new scan results

## Testing Steps

### Test 1: Basic State Preservation
1. Go to Сканирование page
2. Upload/paste an image with a table code (ТОРГ-12, Message, etc.)
3. Wait for scan results to appear
4. Note the preview image, recognized text, and available buttons
5. Click "Открыть форму" button
6. On the form page, click "← Назад"
7. **Expected**: Scan results are still displayed with preview, text, and buttons

### Test 2: State Clearing via Top Menu
1. Scan a code (follow steps 1-3 from Test 1)
2. Click "Главная" in top menu
3. Go back to "Сканировать" 
4. **Expected**: Scan window is clean, no previous results shown

### Test 3: State Clearing via Top Menu (other tabs)
1. Scan a code
2. Click "Создать код" in top menu
3. Go back to "Сканировать"
4. **Expected**: Scan window is clean

### Test 4: Multiple Form Navigations
1. Scan a table code
2. Click "Открыть форму"
3. Click "← Назад"
4. **Expected**: Results preserved
5. Click "Открыть форму" again
6. Click "← Назад" again
7. **Expected**: Results still preserved

### Test 5: Clear Button
1. Scan a code
2. Click "Очистить" button
3. **Expected**: All results cleared
4. Click browser back button
5. **Expected**: No state restoration (state was cleared)

### Test 6: Excel Button Preservation
1. Scan a table code (ТОРГ-12, Message, etc.)
2. Verify "Сохранить в Excel" button is visible
3. Click "Открыть форму"
4. Click "← Назад"
5. **Expected**: "Сохранить в Excel" button is still visible and functional

### Test 7: Non-table Codes
1. Scan a non-table code (regular QR/barcode)
2. Note that "Открыть форму" button is not visible
3. Navigate away and back
4. **Expected**: No preservation attempted (no form to open)

### Test 8: Browser Refresh
1. Scan a code
2. Refresh the page (F5 or Ctrl+R)
3. **Expected**: Scan state is cleared (sessionStorage persists but flag is not set)

## Technical Details

### SessionStorage Keys
- `scanWindowState`: Stores complete scan state as JSON
  - `previewSrc`: Image data URL
  - `text`: Recognized text
  - `codeType`: Display text for code type
  - `fileInfoText`: File size info
  - `openFormHref`: URL for "Открыть форму" button
  - `openFormVisible`: Boolean for button visibility
  - `openExcelVisible`: Boolean for Excel button visibility
  - `excelData`: Object with text and form_type for Excel export
  - `previewVisible`: Boolean for preview container visibility
  - `resultVisible`: Boolean for result card visibility

- `fromFormNavigation`: Flag indicating back navigation from form ('true' or removed)

### Browser Compatibility
- Uses sessionStorage (IE8+, all modern browsers)
- State is cleared when tab/browser is closed
- State is not shared between tabs
