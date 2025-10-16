from datetime import datetime

def format_date(d: datetime) -> str:
    return d.strftime("%d.%m.%Y %H:%M:%S")