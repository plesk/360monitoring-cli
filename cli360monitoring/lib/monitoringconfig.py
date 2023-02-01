
#!/usr/bin/env python3

import os
import configparser

from .functions import printError
from .bcolors import bcolors

class MonitoringConfig(object):

    def __init__(self):
        self.filename = '360monitoring.ini'
        self.endpoint = 'https://api.monitoring360.io/v1/'
        self.api_key = ''
        self.max_items = 5000
        self.threshold_uptime = 99.0
        self.threshold_ttfb = 1.0
        self.threshold_free_diskspace = 20.0

        self.loadFromFile()

    def headers(self):
        """Set headers for http requests"""

        if self.api_key:
            return {
                "Authorization": "Bearer " + self.api_key
            }
        else:
            printError("ERROR: No API key specified in " + self.filename + ". Please run \"360monitoring config --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.")
            return {}

    def loadFromFile(self):
        """Read API endpoint and API key from config file"""

        if os.path.isfile(self.filename):
            parser = configparser.ConfigParser()
            parser.read(self.filename)

            if 'Connection' in parser.sections():
                if 'endpoint' in parser['Connection']:
                    self.endpoint = parser['Connection']['endpoint']

                if 'api-key' in parser['Connection']:
                    self.api_key = parser['Connection']['api-key']

                if 'max-items' in parser['Connection']:
                    self.max_items = parser['Connection']['max-items']

            if 'Thresholds' in parser.sections():
                if 'min-uptime-percent' in parser['Thresholds']:
                    self.threshold_uptime = parser['Thresholds']['min-uptime-percent']

                if 'max-time-to-first-byte' in parser['Thresholds']:
                    self.threshold_ttfb = parser['Thresholds']['max-time-to-first-byte']

                if 'min-free-diskspace-percent' in parser['Thresholds']:
                    self.threshold_free_diskspace = parser['Thresholds']['min-free-diskspace-percent']

    def saveToFile(self):
        """Save settings to config file"""

        parser = configparser.ConfigParser()
        parser['Connection'] = {
            'api-key': self.api_key,
            'endpoint': self.endpoint,
            'max-items': self.max_items
        }
        parser['Thresholds'] = {
            'min-uptime-percent': self.threshold_uptime,
            'max-time-to-first-byte': self.threshold_ttfb,
            'min-free-diskspace-percent': self.threshold_free_diskspace,
        }

        with open(self.filename, 'w') as config_file:
            parser.write(config_file)

    def print(self):
        """Print current settings"""

        if os.path.isfile(self.filename):
            print('config file:               ', self.filename)
        else:
            print(f"config file:                {bcolors.WARNING}" + self.filename + f" does not exist. Please run \"360monitoring config --api-key YOUR_API_KEY\" to configure.{bcolors.ENDC}")
        print()
        print('Connection')
        print('----------')
        print('endpoint:                  ', self.endpoint)
        if self.api_key:
            print('api-key:                   ', self.api_key)
        else:
            print(f"api-key:                    {bcolors.FAIL}No API key specified in " + self.filename + f". Please run \"360monitoring config --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.{bcolors.ENDC}")
        print('max items:                 ', self.max_items)
        print()
        print('Thresholds')
        print('----------')
        print('min-uptime-percent:        ', self.threshold_uptime)
        print('max-time-to-first-byte:    ', self.threshold_ttfb)
        print('min-free-diskspace-percent:', self.threshold_free_diskspace)
