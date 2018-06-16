from plugins.login_test import LoginCheck
from discord_client import DiscordClient

def handle(*args, **kwargs):
    client = DiscordClient()

    LoginCheck(discord_client=client).run()

    client.close()
