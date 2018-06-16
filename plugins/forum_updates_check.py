import datetime
import os

import boto3
import discord
import requests
from defusedxml.ElementTree import fromstring

from plugins.base import BasePlugin

ANNOUNCEMENTS_URL = "https://community.blackdesertonline.com/index.php?forums/news-announcements.181/index.rss"
PATCH_NOTES_URL = "https://community.blackdesertonline.com/index.php?forums/patch-notes.5/index.rss"
EVENTS_URL = "https://community.blackdesertonline.com/index.php?forums/events.6/index.rss"


class BaseForumUpdateCheck(BasePlugin):
    FORUM_RSS_URL = None
    MESSAGE_TITLE = ""
    ATTRIBUTE_MAPPING = {
        "lastPublishedDate": str
    }

    @property
    def _date_format(self):
        return "%a, %d %b %Y %H:%M:%S %z"

    def _parse_date_string(self, date):
        return datetime.datetime.strptime(date, self._date_format)

    @property
    def last_published_date(self):
        item = self.get_item()

        if not item:
            return None

        return self._parse_date_string(item['Item']['lastPublishedDate']['S'])

    def parse_response(self, response):
        et = fromstring(response.text)
        last_published = self.last_published_date
        latest_published = None
        new_updates = []

        for item in et.find('channel').findall('item'):
            # Each item is a forum post
            pub_date = self._parse_date_string(item.find('pubDate').text)

            if latest_published is None or pub_date > latest_published:
                latest_published = pub_date

            if pub_date > last_published:
                new_updates.append(item.find('link').text)
            else:
                # The posts are sorted by date, we can exit early once we hit the old posts
                break

        if latest_published is None:
            print("Could not retrieve latest post")
            return

        if last_published is None:
            self.create_item(lastPublishedDate=latest_published.strftime(self._date_format))
        elif latest_published > last_published:
            self.update_item(lastPublishedDate=latest_published.strftime(self._date_format))

            # Broadcast all new posts
            for link in new_updates:
                self.discord.broadcast_message(content="@here **{}** \n {}".format(self.MESSAGE_TITLE, link))

    def run(self):
        if self.FORUM_RSS_URL is None:
            raise NotImplementedError("No FORUM_RSS_URL defined")

        print("Running {}...".format(self.PLUGIN_TYPE))
        response = requests.get(self.FORUM_RSS_URL)

        self.parse_response(response)
        print("Completed {}".format(self.PLUGIN_TYPE))


class AnnouncementUpdateCheck(BaseForumUpdateCheck):
    PLUGIN_TYPE = 'announcement-check'
    FORUM_RSS_URL = "https://community.blackdesertonline.com/index.php?forums/news-announcements.181/index.rss"
    MESSAGE_TITLE = "New News & Announcements"


class PatchNoteUpdateCheck(BaseForumUpdateCheck):
    PLUGIN_TYPE = 'patch-note-check'
    FORUM_RSS_URL = "https://community.blackdesertonline.com/index.php?forums/patch-notes.5/index.rss"
    MESSAGE_TITLE = "New Patch Notes"


class EventUpdateCheck(BaseForumUpdateCheck):
    PLUGIN_TYPE = 'event-check'
    FORUM_RSS_URL = "https://community.blackdesertonline.com/index.php?forums/events.6/index.rss"
    MESSAGE_TITLE = "New Events"
