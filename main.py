import configparser
from os import path

import discord

from core import consts

_config = configparser.ConfigParser()
_config.read(path.join(consts.cwd(), 'config.ini'))


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(_config['discord']['token'])
