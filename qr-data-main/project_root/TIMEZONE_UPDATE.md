# Timezone Update - Moscow Time (UTC+3) Implementation

## Overview
Modified the application to display all timestamps in Moscow timezone (UTC+3) instead of UTC. This affects all user-visible timestamp fields including history records and account creation dates.

## Changes Made

### 1. New Utility Module: `app/utils/timezone.py`
Created a new timezone conversion utility that:
- Defines Moscow timezone as UTC+3
- Provides `utc_to_moscow()` function to convert UTC timestamps to Moscow time
- Handles edge cases (empty strings, invalid formats)
- Returns formatted string in "YYYY-MM-DD HH:MM:SS" format

```python
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

def utc_to_moscow(timestamp_str):
    """Convert UTC timestamp string to Moscow time (UTC+3)"""
    if not timestamp_str:
        return ""
    
    try:
        dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_moscow = dt_utc.astimezone(MOSCOW_TZ)
        return dt_moscow.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp_str
```

### 2. Flask App Integration: `app/__init__.py`
- Imported the `utc_to_moscow` function
- Registered it as a Jinja2 template filter
- Filter name: `utc_to_moscow`

### 3. Template Updates

#### `app/templates/history.html`
Changed line displaying creation timestamp:
```jinja
Before: <td>{{ r.created_at }}</td>
After:  <td>{{ r.created_at | utc_to_moscow }}</td>
```

#### `app/templates/admin_users.html`
Changed line displaying user creation date:
```jinja
Before: <td>{{ u.created_at }}</td>
After:  <td>{{ u.created_at | utc_to_moscow }}</td>
```

## Database Storage
- Timestamps remain stored in UTC in SQLite database
- CURRENT_TIMESTAMP still stores UTC time
- Conversion happens only during display (view layer)
- No changes to database schema or storage logic

## Time Conversion Examples

| UTC Time           | Moscow Time (UTC+3) |
|--------------------|---------------------|
| 2024-01-15 12:00:00 | 2024-01-15 15:00:00 |
| 2024-06-20 09:30:00 | 2024-06-20 12:30:00 |
| 2024-12-31 21:00:00 | 2025-01-01 00:00:00 |
| 2024-03-10 00:00:00 | 2024-03-10 03:00:00 |

## Testing
Created test file `test_timezone_integration.py` to verify:
1. Timezone conversion utility works correctly
2. Flask app initializes with filter registered
3. Templates updated to use the filter
4. All edge cases handled properly

## Affected Views
- **History Page** (`/history`): Displays "created_at" in Moscow time
- **Admin Users Page** (`/admin/users`): Displays user "created_at" in Moscow time

## Backward Compatibility
- Existing database records are not modified
- System continues to store times in UTC
- Only display format changes to Moscow time
- Filter gracefully handles missing or malformed timestamps

## Implementation Notes
- Uses Python's standard `datetime` library
- No external dependencies required
- Timezone offset is fixed at +3 hours (does not account for DST)
- Moscow officially uses permanent UTC+3 without DST changes since 2014
- Filter can be reused in any template with `{{ timestamp | utc_to_moscow }}`

## Files Modified
1. `app/__init__.py` - Added filter registration
2. `app/templates/history.html` - Applied filter to created_at
3. `app/templates/admin_users.html` - Applied filter to created_at

## Files Created
1. `app/utils/__init__.py` - Package marker
2. `app/utils/timezone.py` - Timezone conversion utility
3. `test_timezone_integration.py` - Integration tests
4. `TIMEZONE_UPDATE.md` - This documentation
