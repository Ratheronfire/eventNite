from datetime import datetime, timedelta, timezone
from typing import Optional

from discord import VoiceChannel, StageChannel, ScheduledEventLocation


class Event(dict):
    def __init__(self,
                 name: str,
                 date: datetime,
                 hours: int,
                 location: str | int | VoiceChannel | StageChannel | ScheduledEventLocation,
                 subscriber_count: Optional[int] = None,
                 creator_id: Optional[int] = None,
                 id: Optional[int] = None
                 ):
        dict.__init__(self, name=name,
                      date=date.timestamp(),
                      hours=hours,
                      location=location,
                      subscriber_count=subscriber_count,
                      creator_id=creator_id,
                      id=id)
        self['tz_offset'] = date.utcoffset().seconds
        self['tz_name'] = date.tzname()

    @property
    def name(self) -> str:
        return self['name']

    @name.setter
    def name(self, value: str):
        self['name'] = value

    @property
    def date(self) -> datetime:
        tz = timezone(timedelta(seconds=self['tz_offset']), self['tz_name'])
        date = datetime.fromtimestamp(self['date'], tz=tz)
        return date

    @date.setter
    def date(self, value: datetime):
        self['date'] = value.timestamp()

    @property
    def hours(self) -> int:
        return int(self['hours'])

    @hours.setter
    def hours(self, value: int):
        self['hours'] = value

    @property
    def location(self) -> str | int | VoiceChannel | StageChannel | ScheduledEventLocation:
        return self['location']

    @location.setter
    def location(self, value: str | int | VoiceChannel | StageChannel | ScheduledEventLocation):
        self['location'] = value

    @property
    def subscriber_count(self) -> int:
        return self['subscriber_count']

    @subscriber_count.setter
    def subscriber_count(self, value: int):
        self['subscriber_count'] = value

    @property
    def creator_id(self) -> int:
        return self['creator_id']

    @creator_id.setter
    def creator_id(self, value: int):
        self['creator_id'] = value

    @property
    def id(self) -> int:
        return self['id']

    @id.setter
    def id(self, value: int):
        self['id'] = value

    @property
    def end_date(self) -> datetime:
        return self.date + timedelta(hours=self.hours)
