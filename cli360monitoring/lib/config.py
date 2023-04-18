
#!/usr/bin/env python3

import os
import configparser

from .functions import printError
from .bcolors import bcolors

class Config(object):

    def __init__(self, version: str):
        self.version = version
        self.filename = '360monitoring.ini'
        self.endpoint = 'https://api.monitoring360.io/v1/'
        self.api_key = ''
        self.usertoken = ''
        self.max_items = 5000
        self.debug = False
        self.readonly = False
        self.hide_ids = False
        self.delimiter = ','
        self.last_version_check = ''

        self.threshold_uptime = 99.0
        self.threshold_ttfb = 1.0
        self.threshold_free_diskspace = 20.0
        self.threshold_cpu_usage = 80.0
        self.threshold_mem_usage = 80.0
        self.threshold_disk_usage = 80.0

        self.loadFromFile()

    def headers(self):
        """Set headers for http requests"""

        if self.api_key:
            return {
                'Authorization': 'Bearer ' + self.api_key,
                'User-Agent': '360 Monitoring CLI ' + self.version,
            }
        else:
            printError('ERROR: No API key specified in ' + self.filename + ". Please run \"360monitoring config save --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.")
            return {}

    def params(self, tags:str = ''):
        """Set params for http requests"""

        params = {
                'perpage': self.max_items,
                'api_mode': 'cli_' + self.version
            }

        if tags:
            params['tags'] = tags

        return params

    def loadFromFile(self):
        """Read API endpoint and API key from config file"""

        if os.path.isfile(self.filename):
            parser = configparser.ConfigParser()
            parser.read(self.filename)

            if 'General' in parser.sections():
                if 'last-version-check' in parser['General']:
                    self.last_version_check = parser['General']['last-version-check']

            if 'Connection' in parser.sections():
                if 'endpoint' in parser['Connection']:
                    self.endpoint = parser['Connection']['endpoint']

                if 'api-key' in parser['Connection']:
                    self.api_key = parser['Connection']['api-key']

                if 'usertoken' in parser['Connection']:
                    self.usertoken = parser['Connection']['usertoken']

                if 'max-items' in parser['Connection']:
                    self.max_items = parser['Connection']['max-items']

                if 'hide-ids' in parser['Connection']:
                    self.hide_ids = (parser['Connection']['hide-ids'] == 'True')

                if 'debug' in parser['Connection']:
                    self.debug = (parser['Connection']['debug'] == 'True')

                if 'readonly' in parser['Connection']:
                    self.readonly = (parser['Connection']['readonly'] == 'True')

            if 'Thresholds' in parser.sections():
                if 'min-uptime-percent' in parser['Thresholds']:
                    self.threshold_uptime = parser['Thresholds']['min-uptime-percent']

                if 'max-time-to-first-byte' in parser['Thresholds']:
                    self.threshold_ttfb = parser['Thresholds']['max-time-to-first-byte']

                if 'min-free-diskspace-percent' in parser['Thresholds']:
                    self.threshold_free_diskspace = parser['Thresholds']['min-free-diskspace-percent']

                if 'max-cpu-usage-percent' in parser['Thresholds']:
                    self.threshold_cpu_usage = parser['Thresholds']['max-cpu-usage-percent']

                if 'max-mem-usage-percent' in parser['Thresholds']:
                    self.threshold_mem_usage = parser['Thresholds']['max-mem-usage-percent']

                if 'max-disk-usage-percent' in parser['Thresholds']:
                    self.threshold_disk_usage = parser['Thresholds']['max-disk-usage-percent']

    def saveToFile(self, printInfo : bool = True):
        """Save settings to config file"""

        parser = configparser.ConfigParser()
        parser['General'] = {
            'last-version-check': self.last_version_check,
        }
        parser['Connection'] = {
            'api-key': self.api_key,
            'usertoken': self.usertoken,
            'endpoint': self.endpoint,
            'max-items': self.max_items,
            'hide-ids': self.hide_ids,
            'debug': self.debug,
            'readonly': self.readonly,
        }
        parser['Thresholds'] = {
            'min-uptime-percent': self.threshold_uptime,
            'max-time-to-first-byte': self.threshold_ttfb,
            'min-free-diskspace-percent': self.threshold_free_diskspace,
            'max-cpu-usage-percent': self.threshold_cpu_usage,
            'max-mem-usage-percent': self.threshold_mem_usage,
            'max-disk-usage-percent': self.threshold_disk_usage,
        }

        with open(self.filename, 'w') as config_file:
            parser.write(config_file)

        if printInfo:
            print('Saved settings to', self.filename)

    def print(self):
        """Print current settings"""

        if os.path.isfile(self.filename):
            print('config file:'.ljust(30), self.filename)
        else:
            print('config file:'.ljust(30) + f"{bcolors.WARNING}" + self.filename + f" does not exist. Please run \"360monitoring config save --api-key YOUR_API_KEY\" to configure.{bcolors.ENDC}")

        print('CLI version:'.ljust(30), self.version)
        print()
        print('Connection')
        print('----------')
        print('endpoint:'.ljust(30), self.endpoint)

        if self.api_key:
            print('api-key:'.ljust(30), self.api_key)
        else:
            print('api-key:'.ljust(30) + f"{bcolors.FAIL}No API key specified in " + self.filename + f". Please run \"360monitoring config save --api-key YOUR_API_KEY\" to connect to your 360 Monitoring account.{bcolors.ENDC}")

        if self.usertoken:
            print('usertoken:'.ljust(30), self.usertoken)
        else:
            print('usertoken:'.ljust(30) + f"{bcolors.FAIL}No usertoken specified in " + self.filename + f". Please run \"360monitoring config save --usertoken YOUR_TOKEN\" to use it for creating magic links.{bcolors.ENDC}")

        print('max items:'.ljust(30), self.max_items)
        print('hide ids:'.ljust(30), self.hide_ids)
        print('debug:'.ljust(30), self.debug)
        print('readonly:'.ljust(30), self.readonly)
        print()
        print('Thresholds')
        print('----------')
        print('min-uptime-percent:'.ljust(30), self.threshold_uptime)
        print('max-time-to-first-byte:'.ljust(30), self.threshold_ttfb)
        print('min-free-diskspace-percent:'.ljust(30), self.threshold_free_diskspace)
        print('max-cpu-usage-percent:'.ljust(30), self.threshold_cpu_usage)
        print('max-mem-usage-percent:'.ljust(30), self.threshold_mem_usage)
        print('max-disk-usage-percent:'.ljust(30), self.threshold_disk_usage)
