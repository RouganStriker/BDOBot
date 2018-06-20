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
PLAY_TOKEN_URL = "https://blackdesertonline.com/launcher/l/api/CreatePlayToken.json"


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
        elif item['Item']['isOnline']['BOOL'] != isOnline:
            # Status changed
            self.update_item(isOnline=isOnline)

            embed = discord.Embed(
                title='Login Status',
                description='The game service is currently {}'.format("ONLINE" if isOnline else "OFFLINE"),
                colour=discord.Color.green() if isOnline else discord.Color.red()
            )

            print("Status changed to {}, broadcasting...".format(isOnline))
            self.discord.broadcast_message(content="@here **Status Notification**", embed=embed)

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
        print("Performing Login server test...")
        form_data = self.get_creds()
        response = requests.post(LOGIN_URL, data=form_data)

        # Grab token from login response
        play_token = response.json().get('result', {}).get('token')

        if play_token is not None:
            response = requests.post(PLAY_TOKEN_URL, data={
                "token": play_token,
                "lang": "EN",
                "region": "NA"
            })

            # Check play token creation
            self.parse_response(response)

        print("Completed Login server test")
