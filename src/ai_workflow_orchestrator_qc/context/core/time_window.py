from datetime import timedelta
from ..config import Config


def resolve_time_windows(event_time):
    return {
        "maintenance": {
            "from": event_time - timedelta(days=Config.MAINTENANCE_WINDOW_DAYS),
            "to": event_time
        },
        "operator_notes": {
            "from": event_time - timedelta(hours=Config.OPERATOR_NOTES_WINDOW_HOURS),
            "to": event_time
        }
    }
