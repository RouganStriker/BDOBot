from discord_client import DiscordClient
from plugins.login_test import LoginCheck
from plugins.forum_updates_check import AnnouncementUpdateCheck, EventUpdateCheck, PatchNoteUpdateCheck
from plugins.patch_update_check import PatchUpdateCheck


def handle(*args, **kwargs):
    client = DiscordClient()
    client.initialize()

    try:
        LoginCheck(discord_client=client).run()
        AnnouncementUpdateCheck(discord_client=client).run()
        EventUpdateCheck(discord_client=client).run()
        PatchNoteUpdateCheck(discord_client=client).run()
        PatchUpdateCheck(discord_client=client).run()
    finally:
        client.close()
