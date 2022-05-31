from datetime import timedelta, timezone, datetime

from actions_toolkit import core


def now():
    tz = timezone(timedelta(hours=+8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')


def info(s: str = ''):
    core.info(f'[{now()}] {s}')


def warning(s: str = ''):
    core.warning(f'[{now()}] {s}')


def error(s: str = ''):
    core.info(f'[{now()}] {s}')


def set_failed(s: str = ''):
    core.set_failed(f'[{now()}] {s}')
