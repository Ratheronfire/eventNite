import configparser
from datetime import datetime
from os import path

import discord
from discord import option

from core import consts
from core.converters import DateTimeString
from core.objects.event import Event

_config = configparser.ConfigParser()
_config.read(path.join(consts.cwd(), 'config.ini'))


intents = discord.Intents.default()
intents.members = True


bot = discord.Bot(
    # debug_guilds=[...],
    description="An example to showcase how to extract info about users.",
    intents=intents,
)

events = consts.read_event_file()


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


@bot.slash_command(name="newevent", description="Schedules a new event.")
@option("event_name", description="The name of the event.")
@option("event_date", description="The date and time of the event (time zone optional).")
@option("hours", description="The length of the event in hours (default 1).")
async def new_event(ctx: discord.ApplicationContext, event_name: str, event_date: DateTimeString, hours=1):
    if event_date < datetime.now():
        await ctx.respond('Cannot create events in the past.')
        return

    event = Event(event_name, event_date, hours)

    await ctx.channel.guild.create_scheduled_event(
        name=event_name,
        start_time=event.date,
        end_time=event.end_date,
        location=int(_config['discord']['voice_channel_id'])
    )

    event_list = consts.read_event_file() + [event]
    consts.write_event_file(event_list)

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


@bot.slash_command(name="userinfo", description="Gets info about a user.")
async def info(ctx: discord.ApplicationContext, user: discord.Member = None):
    user = (
        user or ctx.author
    )  # If no user is provided it'll use the author of the message
    embed = discord.Embed(
        fields=[
            discord.EmbedField(name="ID", value=str(user.id), inline=False),  # User ID
            discord.EmbedField(
                name="Created",
                value=discord.utils.format_dt(user.created_at, "F"),
                inline=False,
            ),  # When the user's account was created
        ],
    )
    embed.set_author(name=user.name)
    embed.set_thumbnail(url=user.display_avatar.url)

    if user.colour.value:  # If user has a role with a color
        embed.colour = user.colour

    if isinstance(user, discord.User):  # Checks if the user in the server
        embed.set_footer(text="This user is not in this server.")
    else:  # We end up here if the user is a discord.Member object
        embed.add_field(
            name="Joined",
            value=discord.utils.format_dt(user.joined_at, "F"),
            inline=False,
        )  # When the user joined the server

    await ctx.respond(embeds=[embed])  # Sends the embed


bot.run(_config['discord']['token'])
