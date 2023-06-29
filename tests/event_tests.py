import asyncio
import os
from datetime import datetime, timedelta
from os import path

from pyfakefs.fake_filesystem_unittest import TestCase
from unittest.mock import patch

from core import consts
from core.eventmanager import EventManager
from core.utils.config_utils import gettz


class MockClass(object):
    pass


# https://stackoverflow.com/a/46324983
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# noinspection PyTypeChecker
class EventTestCase(TestCase):
    event_manager: EventManager

    mock_discord_context: MockClass
    mock_discord_events = []

    async def create_scheduled_event(self,
                                     name,
                                     description,
                                     reason,
                                     start_time,
                                     end_time,
                                     location):
        class MockScheduledEvent:
            id: int
            subscriber_count: int
            creator_id: int

            def __init__(self, id: int, subscriber_count: int, creator_id: int):
                self.id = id
                self.subscriber_count = subscriber_count
                self.creator_id = creator_id

        mock_event = MockClass()
        mock_event.name = name
        mock_event.description = description
        mock_event.reason = reason
        mock_event.start_time = start_time
        mock_event.end_time = end_time
        mock_event.location = location
        mock_event.subscriber_count = 0
        mock_event.creator_id = 0
        mock_event.id = 0

        async def remove_mock_event(reason: str):
            self.mock_discord_events.remove(mock_event)
        mock_event.cancel = remove_mock_event

        self.mock_discord_events.append(mock_event)

        async def edit_mock_event(name, description, start_time, end_time, reason):
            mock_event.name = name
            mock_event.description = description
            mock_event.start_time = start_time
            mock_event.end_time = end_time

            return mock_event

        mock_event.edit = edit_mock_event

        return MockScheduledEvent(1, 0, 1)

    def create_mock_context(self):
        self.mock_discord_context = MockClass()

        self.mock_discord_context.channel = MockClass()
        self.mock_discord_context.channel.guild = MockClass()
        self.mock_discord_context.channel.guild.create_scheduled_event = self.create_scheduled_event
        self.mock_discord_context.channel.guild.scheduled_events = self.mock_discord_events

        self.mock_discord_context.interaction = MockClass()
        self.mock_discord_context.interaction.user = MockClass()
        self.mock_discord_context.interaction.user.name = 'MockUser'

    def setUp(self):
        self.setUpPyfakefs()

        self.create_mock_context()

        os.makedirs(consts.cwd())
        os.makedirs(consts.data_folder())

        consts.write_event_file([])

        with open(path.join(consts.cwd(), 'config.ini'), 'w') as config_file:
            config_file.write('[globals]\n'
                              'tz = America\\New_York\n\n'
                              '[discord]\n'
                              'token = \n'
                              'invite_url =\n'
                              'voice_channel_id = 0')

        self.event_manager = EventManager()
        self.mock_discord_events = []

    @async_test
    async def test_add_event(self):
        event_date = datetime.now(gettz()) + timedelta(hours=1)

        await self.event_manager.add_new_event(self.mock_discord_context, 'Test Event', event_date)

        assert len(self.mock_discord_events) == 1
        assert self.mock_discord_events[0].name == 'Test Event'

        events_file = consts.read_event_file()
        assert len(events_file) == 1
        assert events_file[0]['name'] == 'Test Event'

    @async_test
    async def test_delete_event(self):
        event_date = datetime.now(gettz()) + timedelta(hours=1)

        await self.event_manager.add_new_event(self.mock_discord_context, 'Test Event', event_date)
        self.mock_discord_context.channel.guild.scheduled_events = self.mock_discord_events

        assert len(self.mock_discord_events) == 1

        events_file = consts.read_event_file()
        assert len(events_file) == 1

        await self.event_manager.delete_event(self.mock_discord_context, 'Test Event')

        assert len(self.mock_discord_events) == 0

        events_file = consts.read_event_file()
        assert len(events_file) == 0

    @async_test
    async def test_edit_event(self):
        event_date = datetime.now(gettz()) + timedelta(hours=1)

        await self.event_manager.add_new_event(self.mock_discord_context, 'Test Event', event_date)
        self.mock_discord_context.channel.guild.scheduled_events = self.mock_discord_events

        assert len(self.mock_discord_events) == 1
        assert self.mock_discord_events[0].name == 'Test Event'

        events_file = consts.read_event_file()
        assert len(events_file) == 1
        assert events_file[0]['name'] == 'Test Event'

        event_date += timedelta(hours=1)

        await self.event_manager.edit_event(self.mock_discord_context,
                                            event_name='Test Event',
                                            new_event_name='Edited Event',
                                            event_date=event_date,
                                            description='Edited description.',
                                            hours=3)

        assert len(self.mock_discord_events) == 1
        assert self.mock_discord_events[0].description == 'Edited description.'

        events_file = consts.read_event_file()
        assert len(events_file) == 1
        assert events_file[0]['name'] == 'Edited Event'
        assert events_file[0]['date'] == event_date.timestamp()
        assert events_file[0]['hours'] == 3

    @async_test
    async def test_add_duplicate_event(self):
        event_date = datetime.now(gettz()) + timedelta(hours=1)

        await self.event_manager.add_new_event(self.mock_discord_context, 'Test Event', event_date)

        assert len(self.mock_discord_events) == 1
        assert self.mock_discord_events[0].name == 'Test Event'

        events_file = consts.read_event_file()
        assert len(events_file) == 1
        assert events_file[0]['name'] == 'Test Event'

        with self.assertRaises(ValueError) as context:
            await self.event_manager.add_new_event(self.mock_discord_context, 'Test Event', event_date)

            assert 'An event with that name already exists.' in context.exception

        assert len(self.mock_discord_events) == 1

        events_file = consts.read_event_file()
        assert len(events_file) == 1

    @async_test
    async def test_try_add_past_event(self):
        with self.assertRaises(ValueError) as context:
            await self.event_manager.add_new_event(self.mock_discord_context,
                                                   'Test Event',
                                                   datetime(2023, 1, 1, 0, tzinfo=gettz()))

            assert 'Cannot create events in the past.' in context.exception

        assert len(self.mock_discord_events) == 0

        events_file = consts.read_event_file()
        assert len(events_file) == 0
