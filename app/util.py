from datetime import timedelta, timezone, datetime


def now():
    tz = timezone(timedelta(hours=+8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
