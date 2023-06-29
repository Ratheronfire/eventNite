from datetime import datetime, time

from dateutil.parser import parse
from dateutil.tz import tz, gettz
from discord.ext import commands
from discord.ext.commands import Context


def is_dst(time: datetime) -> bool:
    return time.dst() == 1


# TODO: Figure out more robust timezone logic.
tzinfos = {
    'UT': gettz('GMT'),
    'EST': -18000,
    'EDT': -14400,
    'ET': -18000 if is_dst(datetime.now()) else -14400,
    'CST': -21600,
    'CDT': -18000,
    'CT': -21600 if is_dst(datetime.now()) else -18000,
    'MST': -25200,
    'MDT': -21600,
    'MT': -25200 if is_dst(datetime.now()) else -21600,
    'PST': -28800,
    'PDT': -25200,
    'PT': -28800 if is_dst(datetime.now()) else -25200,
}


def add_tzinfo_to_datetime(time: datetime | str) -> datetime:
    return parse(time, tzinfos=tzinfos)
