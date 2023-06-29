import configparser
import logging
from datetime import datetime
from os import path

import discord
from discord import option, ScheduledEventStatus
from discord.errors import Forbidden

from core import consts
from core.converters import add_tzinfo_to_datetime
from core.eventmanager import EventManager
from core.utils import config_utils

event_manager = EventManager()

_config = configparser.ConfigParser()
_config.read(path.join(consts.cwd(), 'config.ini'))


intents = discord.Intents.default()
intents.members = True


bot = discord.Bot(
    # debug_guilds=[...],
    description="A simple scheduler for event nights.",
    intents=intents,
)

events = consts.read_event_file()


async def get_scheduled_event_names(ctx: discord.AutocompleteContext):
    return [e.name for e in ctx.bot.guilds[0].scheduled_events if e.status == ScheduledEventStatus.scheduled]


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.slash_command(name="newevent", description="Schedules a new event.")
@option("event_name", description="The name of the event.")
@option("event_date", description="The date and time of the event (time zone required).")
@option("description", description="An optional description for the event.")
@option("hours", description="The length of the event in hours (default 1).")
async def new_event(ctx: discord.ApplicationContext,
                    event_name: str,
                    event_date: str,
                    description='',
                    hours=1):
    try:
        event_date = add_tzinfo_to_datetime(event_date)

        print(f'Attempting to add event {event_name} at {event_date}.')

        if event_date < datetime.now(config_utils.gettz()):
            await ctx.respond('Cannot create events in the past.')
            return

        event, message = await event_manager.add_new_event(ctx, event_name, event_date, description, hours)
    except Exception as exc:
        logging.exception(exc)

        if 'can\'t compare offset-naive and offset-aware datetimes' in str(exc):
            await ctx.respond('Unable to parse event time; Either you didn\'t provide a timezone or the bot '
                              'doesn\'t know the timezone you provided.')
        else:
            await ctx.respond(f'Failed to add event ({exc})')

        return

    if not event:
        await ctx.respond(f'Failed to add event ({message})')

    embed = discord.Embed(
        title="New Event Added",
        fields=[
            discord.EmbedField(name="Event Name", value=event_name, inline=False),
            discord.EmbedField(
                name="Event Date",
                value=f'{discord.utils.format_dt(event.date, "F")} to {discord.utils.format_dt(event.end_date, "F")}',
                inline=False,
            ),
        ],
    )
    embed.set_author(name=event_name)

    await ctx.respond(embeds=[embed])


@bot.slash_command(name="cancelevent", description="Cancels a scheduled event.")
async def cancel_event(ctx: discord.ApplicationContext,
                       event_name: discord.Option(
                           str,
                           description="The name of the event.",
                           autocomplete=discord.utils.basic_autocomplete(get_scheduled_event_names))):
    try:
        await event_manager.delete_event(ctx, event_name)
    except Forbidden as exc:
        if exc.code == 180000:
            await ctx.respond('That event has already been cancelled.')
            return
    except ValueError as exc:
        logging.exception(exc)

        await ctx.respond(f'Failed to cancel event ({exc})')
        return

    embed = discord.Embed(
        title="Event Cancelled",
        fields=[
            discord.EmbedField(name="Event Name", value=event_name, inline=False)
        ],
    )
    embed.set_author(name=event_name)

    await ctx.respond(embeds=[embed])


bot.run(_config['discord']['token'])
# TODO: Sync event file with existing events
