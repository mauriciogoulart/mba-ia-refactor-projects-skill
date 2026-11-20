from datetime import datetime, timezone


def utcnow():
    """Instante atual em UTC sem fuso, o formato já persistido no banco."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
