from discord_client import DiscordClient
from plugins.login_test import LoginCheck
from plugins.forum_updates_check import AnnouncementUpdateCheck, EventUpdateCheck, PatchNoteUpdateCheck


def handle(*args, **kwargs):
    client = DiscordClient()
    client.initialize()

    try:
        LoginCheck(discord_client=client).run()
        AnnouncementUpdateCheck(discord_client=client).run()
        EventUpdateCheck(discord_client=client).run()
        PatchNoteUpdateCheck(discord_client=client).run()
    finally:
        client.close()
