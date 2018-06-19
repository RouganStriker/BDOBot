import os
import threading
from base64 import b64decode

import asyncio
import boto3
import discord
import requests

token = os.environ.get("DISCORD_TOKEN", None)
CHANNEL_NAME = "announcements"


class DClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}".format(self.user.name))


class DiscordClient(object):
    # Discord Client wrapper

    def __init__(self):
        asyncio.set_event_loop(asyncio.new_event_loop())

        if token is None:
            raise Exception("Missing environment variable DISCORD_TOKEN")

        self.client = DClient()

        environment = os.environ.get("ENVIRONMENT", None)
        self.bot_token = token

        if environment == "AWS":
            # Token is encrypted
            self.bot_token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(token))['Plaintext'].decode('ascii')

        self.broadcast_channels = []

    def initialize(self):
        loop = asyncio.get_event_loop()

        # Start the Bot on a different thread
        self.thread = threading.Thread(target=self.client.run, args=(self.bot_token,))
        self.thread.start()

        self.broadcast_channels = asyncio.run_coroutine_threadsafe(self.get_broadcast_channels(), loop).result()

        print("Found {0} broadcast channels.".format(len(self.broadcast_channels)))

    async def get_broadcast_channels(self):
        await self.client.wait_until_ready()

        channels = []

        print("Connected to {0} servers".format(len(self.client.servers)))

        for server in self.client.servers:
            for channel in server.channels:
                if channel.name.lower() == CHANNEL_NAME:
                    channels.append(channel)

        return channels

    def broadcast_message(self, content=None, embed=None):
        print("Broadcasting message to all clients...")

        loop = self.client.loop

        for channel in self.broadcast_channels:
            asyncio.run_coroutine_threadsafe(self.client.send_message(channel, content=content, embed=embed), loop).result()

    def close(self):
        print("Terminating Discord Client")
        self.client.loop.call_soon_threadsafe(self.client.loop.stop)
        self.thread.join()
