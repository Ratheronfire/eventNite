from datetime import datetime, time

from dateutil.parser import parse
from dateutil.tz import tz, gettz
from discord.ext import commands
from discord.ext.commands import Context

# TODO: Figure out more robust timezone logic.
tzinfos = {
    'UT': gettz('GMT'),
    'EST': -18000,
    'EDT': -14400,
    'CST': -21600,
    'CDT': -18000,
    'MST': -25200,
    'MDT': -21600,
    'PST': -28800,
    'PDT': -25200
}


class DateTimeString(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> datetime:
        return parse(argument, tzinfos=tzinfos)
