from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

def utc_to_moscow(timestamp_str):
    """
    Конвертирует UTC timestamp в московское время (UTC+3)
    
    Принимает timestamp в формате строки (как хранится в SQLite),
    возвращает отформатированную строку в московском времени.
    """
    if not timestamp_str:
        return ""
    
    try:
        dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_moscow = dt_utc.astimezone(MOSCOW_TZ)
        return dt_moscow.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp_str
