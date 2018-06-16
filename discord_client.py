import os
import threading
from base64 import b64decode

import asyncio
import boto3
import discord

token = os.environ.get("DISCORD_TOKEN", None)
CHANNEL_NAME = "announcements"


class DiscordClient(object):
    # Discord Client wrapper

    def __init__(self):
        if token is None:
            raise Exception("Missing environment variable DISCORD_TOKEN")

        self.client = discord.Client()

        environment = os.environ.get("ENVIRONMENT", None)
        self.bot_token = token

        if environment == "AWS":
            # Token is encrypted
            self.bot_token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(token))['Plaintext'].decode('ascii')

        self.client_thread = threading.Thread(target=self.client.run, args=(self.bot_token,))
        self.client_thread.start()

        self.broadcast_channels =  asyncio.run_coroutine_threadsafe(self.get_broadcast_channels, self.client.loop)

        print("Found {0} broadcast channels.".format(len(self.broadcast_channels)))

    async def get_broadcast_channels(self):
        await self.client.wait_until_ready()
        channels = []

        print("Connected to {0} servers".format(len(self.client.servers)))

        for server in self.client.servers:
            for channel in server.channels:
                if channel.name.lower() == CHANNEL_NAME:
                    channels.add(channel)

        return channels

    async def broadcast_message(self, content=None, embed=None):
        await self.client.wait_until_ready()

        for channel in channels:
            await self.client.send_message(channel, content=content, embed=embed)

    def close(self):
        self.client.close()
        self.client_thread.join()
