import datetime
import re

import requests
from defusedxml.ElementTree import fromstring

from plugins.base import BasePlugin


class BaseForumUpdateCheck(BasePlugin):
    FORUM_RSS_URL = None
    MESSAGE_TITLE = ""
    ATTRIBUTE_MAPPING = {
        "lastPublishedDate": str,
        "lastPublishedLink": str,
    }

    @property
    def _date_format(self):
        return "%a, %d %b %Y %H:%M:%S %z"

    def _parse_date_string(self, date):
        return datetime.datetime.strptime(date, self._date_format)

    @property
    def last_published(self):
        item = self.get_item()

        if not item:
            return None

        date = self._parse_date_string(item['Item']['lastPublishedDate']['S'])
        link = item['Item']['lastPublishedLink']['S']

        return date, link

    def is_link_newer(self, old_link, new_link):
        if old_link == new_link:
            return True

        # Check the unique ID at the end of the URL
        old_version = re.search('\.(/d+)/?$', old_link).groups()[0]
        new_version = re.search('\.(/d+)/?$', new_link).groups()[0]

        return int(old_version) < int(new_version)

    def parse_response(self, response):
        et = fromstring(response.text)
        last_published, last_published_link = self.last_published
        latest_published = None
        latest_published_link = None
        new_updates = []

        print("{}: Last forum update was on {}".format(self.PLUGIN_TYPE, last_published))

        for item in et.find('channel').findall('item'):
            # Each item is a forum post
            pub_date = self._parse_date_string(item.find('pubDate').text)
            link = item.find('link').text

            if latest_published is None or (pub_date > latest_published and self.is_link_newer(latest_published_link, link)):
                latest_published = pub_date
                latest_published_link = link
            if pub_date > last_published and self.is_link_newer(last_published_link, link):
                new_updates.append(link)
            else:
                # The posts are sorted by date, we can exit early once we hit the old posts
                break

        if latest_published is None:
            print("Could not retrieve latest post")
            return

        if last_published is None:
            self.create_item(lastPublishedDate=latest_published.strftime(self._date_format),
                             lastPublishedLink=latest_published_link)
        elif latest_published > last_published and latest_published_link != last_published_link:
            print("{}: Found latest update on {}".format(self.PLUGIN_TYPE, latest_published))
            self.update_item(lastPublishedDate=latest_published.strftime(self._date_format),
                             lastPublishedLink=latest_published_link)

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
