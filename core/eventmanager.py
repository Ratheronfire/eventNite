import configparser
import logging
from datetime import datetime, timedelta
from os import path
from typing import Optional

import discord
from discord import HTTPException

from core import consts
from core.objects.event import Event
from core.utils import config_utils


class EventManager:
    events: list[Event]

    def __init__(self):
        self.events = consts.read_event_file()

        self._config = configparser.ConfigParser()
        self._config.read(path.join(consts.cwd(), 'config.ini'))

    async def add_new_event(self, ctx: discord.ApplicationContext,
                            event_name: str,
                            event_date: datetime,
                            description='',
                            hours=1) -> (Event, str):
        if event_date < datetime.now(config_utils.gettz()):
            raise ValueError('Cannot create events in the past.')

        self.events = consts.read_event_file()
        scheduled_events = [e for e in self.events if e['name'] == event_name]

        if len(scheduled_events) > 1:
            raise ValueError(f'Multiple events with name {event_name} were found; Were some added by mistake?')
        elif len(scheduled_events) == 1:
            raise ValueError('An event with that name already exists.')

        if description != '':
            description += '\n\n'
        description += '[Event managed by EventNite]'

        location = int(self._config['discord']['voice_channel_id'])

        event = Event(event_name, event_date, hours, location)
        self.events.append(event)

        scheduled_event = None
        try:
            scheduled_event = await ctx.channel.guild.create_scheduled_event(
                name=event_name,
                description=description,
                start_time=event.date,
                end_time=event.end_date,
                location=location,
                reason=f'EventNite: add_new_event called by {str(ctx.interaction.user)}.'
            )
        except HTTPException as exc:
            logging.exception(exc)

            if 'Cannot schedule event in the past.' in exc.text:
                return None, 'Cannot schedule event in the past.'

        event.id = scheduled_event.id
        event.subscriber_count = scheduled_event.subscriber_count
        event.creator_id = scheduled_event.creator_id

        consts.write_event_file(self.events)

        return event, ''

    async def delete_event(self, ctx: discord.ApplicationContext, event_name: str):
        scheduled_events = [e for e in ctx.channel.guild.scheduled_events if e.name == event_name]

        if len(scheduled_events) > 1:
            raise ValueError(f'Multiple events with name {event_name} were found; Were some added by mistake?')
        elif len(scheduled_events) == 0:
            raise ValueError(f'No active schedule found with name {event_name}.')

        await scheduled_events[0].cancel(reason=f'delete_event called by {str(ctx.interaction.user)}.')

        self.events = consts.read_event_file()
        self.events = [e for e in self.events if e['name'] != event_name]

        consts.write_event_file(self.events)

    async def edit_event(self, ctx: discord.ApplicationContext,
                         event_name: str,
                         new_event_name: Optional[str],
                         event_date: Optional[datetime],
                         description: Optional[str],
                         hours: Optional[int]):
        scheduled_events = [e for e in ctx.channel.guild.scheduled_events if e.name == event_name]

        if len(scheduled_events) != 1:
            raise ValueError(f'No active schedule found with name {event_name}.')

        updated_scheduled_event = await scheduled_events[0].edit(
            name=new_event_name or event_name,
            description=description,
            start_time=event_date,
            end_time=event_date + timedelta(hours=hours),
            reason=f'EventNite: edit_event called by {str(ctx.interaction.user)}'
        )

        self.events = consts.read_event_file()
        self.events = [e for e in self.events if e['name'] != event_name]

        updated_event = Event(updated_scheduled_event.name,
                              updated_scheduled_event.start_time,
                              hours,
                              updated_scheduled_event.location,
                              updated_scheduled_event.subscriber_count,
                              updated_scheduled_event.creator_id,
                              updated_scheduled_event.id)
        self.events.append(updated_event)

        consts.write_event_file(self.events)
