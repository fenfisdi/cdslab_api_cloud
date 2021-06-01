from datetime import datetime


class DateTime:

    @classmethod
    def current_datetime(cls) -> datetime:
        return datetime.utcnow()
