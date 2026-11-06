from datetime import datetime, timezone


def utc_now():
    """Agora em UTC, sem tzinfo (as colunas DateTime do SQLite são ingênuas)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def is_valid_color(color):
    return isinstance(color, str) and len(color) == 7 and color.startswith("#")
