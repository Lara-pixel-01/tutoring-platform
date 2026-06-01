from zoneinfo import ZoneInfo
from flask_login import current_user
from datetime import datetime

def get_user_timezone():
    if current_user.is_authenticated and hasattr(current_user, 'settings') and current_user.settings:
        return current_user.settings.timezone or 'UTC'
    return 'UTC'

def localize_datetime(dt: datetime, tz_name: str = None) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    if tz_name is None:
        tz_name = get_user_timezone()
    if tz_name != 'UTC':
        return dt.astimezone(ZoneInfo(tz_name))
    return dt