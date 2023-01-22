
#!/usr/bin/env python3

import os
import configparser
from lib.functions import print_error
from lib.bcolors import bcolors

class MonitoringConfig(object):

    def __init__(self):
        self.filename = '360monitoring.ini'
        self.section = 'DEFAULT'
        self.endpoint = 'https://api.monitoring360.io/v1/'
        self.api_key = ''
        self.max_items = 5000

        self.load_from_file()

    def headers(self):
        """Set headers for http requests"""

        if self.api_key:
            return {
                "Authorization": "Bearer " + self.api_key
            }
        else:
            print_error("ERROR: No API key specified in " + self.filename + ". Please run \"./360monitoring.py config --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.")
            return {}

    def load_from_file(self):
        """Read API endpoint and API key from config file"""

        if os.path.isfile(self.filename):
            parser = configparser.ConfigParser()
            parser.read(self.filename)

            if 'endpoint' in parser[self.section]:
                self.endpoint = parser[self.section]['endpoint']

            if 'api-key' in parser[self.section]:
                self.api_key = parser[self.section]['api-key']

            if 'max-items' in parser[self.section]:
                self.max_items = parser[self.section]['max-items']

    def save_to_file(self):
        """Save settings to config file"""

        parser = configparser.ConfigParser()
        parser[self.section] = {
            'api-key': self.api_key,
            'endpoint': self.endpoint,
            'max-items': self.max_items
        }
        with open(self.filename, 'w') as config_file:
            parser.write(config_file)

    def print(self):
        if os.path.isfile(self.filename):
            print('config file:', self.filename)
        else:
            print(f"config file: {bcolors.WARNING}" + self.filename + f" does not exist. Please run \"./360monitoring.py config --api-key YOUR_API_KEY\" to configure.{bcolors.ENDC}")
        print('endpoint:   ', self.endpoint)
        if self.api_key:
            print('api-key:    ', self.api_key)
        else:
            print(f"api-key:     {bcolors.FAIL}No API key specified in " + self.filename + f". Please run \"./360monitoring.py config --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.{bcolors.ENDC}")
        print('max items:  ', self.max_items)
