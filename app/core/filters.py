"""
Jinja2 Template Filters
Custom filters for template rendering
"""
from datetime import datetime


def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """
    Format datetime object to string
    
    Args:
        value: datetime object
        format: strftime format string
    
    Returns:
        Formatted datetime string
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    
    return value.strftime(format)


def format_date(value, format='%Y-%m-%d'):
    """Format date object to string"""
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    
    return value.strftime(format)


def format_time(value, format='%H:%M:%S'):
    """Format time to string"""
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    
    return value.strftime(format)


def format_number(value, decimals=2):
    """Format number with specific decimal places"""
    if value is None:
        return "0.00"
    
    try:
        return f"{float(value):.{decimals}f}"
    except:
        return str(value)


def format_percentage(value, decimals=1):
    """Format number as percentage"""
    if value is None:
        return "0.0%"
    
    try:
        return f"{float(value):.{decimals}f}%"
    except:
        return str(value)


def timeago(value):
    """Convert datetime to 'time ago' format"""
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    
    now = datetime.utcnow()
    diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return format_datetime(value, '%Y-%m-%d')
    
def default_zero(value):
    """Return 0 if value is None, otherwise return value"""
    return 0 if value is None else value


def safe_float(value, default=0.0):
    """Safely convert to float, return default if None or invalid"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
    
def clamp(value, min_val=0, max_val=100):
    """Clamp value between min and max"""
    try:
        val = float(value)
        return max(min_val, min(val, max_val))
    except (ValueError, TypeError):
        return min_val