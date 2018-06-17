import requests

import discord
from plugins.base import BasePlugin

PATCH_VERSION_URL = "http://akamai-gamecdn.blackdesertonline.com/live001/game/config/config.patch.version"


class PatchUpdateCheck(BasePlugin):
    PLUGIN_TYPE = "patch-check"
    # Mapping of attribute names to a type
    ATTRIBUTE_MAPPING = {
        "lastPatchVersion": int
    }

    @property
    def last_version(self):
        item = self.get_item()

        if not item:
            return None

        return item['Item']['lastPatchVersion']['N']

    def parse_response(self, response):
        try:
            version = int(response.text)
        except ValueError:
            raise Exception("Failed to parse patch version from response")

        last_version = self.last_version

        if last_version is None:
            self.create_item(lastPatchVersion=version)
        elif version > last_version:
            self.update_item(lastPatchVersion=version)

            # Broadcast patch update
            embed = discord.Embed(
                title='New Patch Notification',
                description='v{}'.format(version),
                colour=discord.Color.blue()
            )

            self.discord.broadcast_message(content="@here Update Notification", embed=embed)

    def run(self):
        print("Running {}...".format(self.PLUGIN_TYPE))
        response = requests.get(PATCH_VERSION_URL)

        self.parse_response(response)
        print("Completed {}".format(self.PLUGIN_TYPE))
