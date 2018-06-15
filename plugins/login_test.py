# Verify that the login works or not
import os

import boto3
import library.request

from base import BasePlugin

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

    def update_status(self, status):
        item = self.get_item()

        if not item:
            # No previous status
            self.create_item(isOnline=status)
        elif item['Item']['isOnline'] != status:
            # Status changed
            self.update_item()

    def run(self):
        form_data = {
            "email": username,
            "password": password
        }
        response = request.post(LOGIN_URL, data=form_data)

        parse_response(response)
