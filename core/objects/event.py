from datetime import datetime, timedelta


class Event(dict):
    def __init__(self, name: str, date: datetime, hours: int):
        dict.__init__(self, name=name, date=date.timestamp(), hours=hours)

    @property
    def name(self) -> str:
        return self['name']

    @property
    def date(self) -> datetime:
        return datetime.fromtimestamp(self['date'])

    @property
    def hours(self) -> int:
        return self['hours']

    @property
    def end_date(self) -> datetime:
        return self.date + timedelta(hours=self.hours)
