# Verify that the login works or not
import os
from base64 import b64decode

import boto3
import discord
import requests

from plugins.base import BasePlugin

username = os.environ.get("BDO_USERNAME", None)
password = os.environ.get("BDO_PASSWORD", None)

LOGIN_URL = "https://www.blackdesertonline.com/launcher/ll/api/Login.json"


class LoginCheck(BasePlugin):
    PLUGIN_TYPE = 'login-check'
    ATTRIBUTE_MAPPING = {
        "isOnline": bool
    }

    def parse_response(self, response):
        content = response.json()
        is_online = None

        if content['api']['code'] == 100:
            # Login online
            is_online = True
        elif content['api']['code'] == 801 and content['api']['additionalInfo']['code'] in ['412', '413', '414', '415']:
            # Maintenance Mode
            is_online = False
        else:
            # Authentication error
            print("Error logging into server.")

        if is_online is not None:
            self.update_status(is_online)

    def update_status(self, isOnline):
        item = self.get_item()

        if not item:
            # No previous status
            self.create_item(isOnline=isOnline)
        elif item['Item']['isOnline'] != isOnline:
            # Status changed
            self.update_item()

            embed = discord.Embed(
                title='Login Status',
                description='The game service is currently {}'.format("ONLINE" if isOnline else "OFFLINE"),
                colour=0xFF0000 if isOnline else 0x00FF00
            )

            self.discord.broadcast_message(content="@here Status Notification", embed=embed)

    def get_creds(self):
        environment = os.environ.get("ENVIRONMENT", None)
        creds = {
            "email": username,
            "password": password
        }

        if environment == "AWS":
            # Credentials are encrypted
            creds = {
                "email": boto3.client('kms').decrypt(CiphertextBlob=b64decode(username))['Plaintext'],
                "password": boto3.client('kms').decrypt(CiphertextBlob=b64decode(password))['Plaintext']
            }

        return creds

    def run(self):
        form_data = self.get_creds()
        response = requests.post(LOGIN_URL, data=form_data)

        self.parse_response(response)
