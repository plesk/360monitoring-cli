#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .monitoringconfig import MonitoringConfig
from .functions import printError, printWarn
from .bcolors import bcolors

class Servers(object):

    def __init__(self, config):
        self.config = config
        self.servers = None
        self.format = 'table'
        self.table = PrettyTable()
        self.table.field_names = ['Server name', 'OS', 'Disk Info']
        self.table.align['Server name'] = 'l'

    def fetchData(self):
        """Retrieve a list of all monitored servers"""

        # if data is already downloaded, use cached data
        if self.servers != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + "servers", params="perpage=" + str(self.config.max_items), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of servers from response
            self.servers = response.json()['servers']
            return True
        else:
            printError("An error occurred:", response.status_code)
            self.servers = None
            return False

    def list(self):
        """Iterate through list of server monitors and print details"""

        if self.fetchData():
            self.printHeader()

            # Iterate through list of monitors and print urls, etc.
            for server in self.servers:
                self.print(server)

            self.printFooter()

    def get(self, pattern: str):
        """Print the data of all server monitors that match the specified server name"""

        if pattern and self.fetchData():
            for server in self.servers:
                if pattern == server['id'] or pattern in server['name']:
                    self.print(server)

    def printHeader(self):
        """Print CSV if CSV format requested"""
        if (self.format == 'csv'):
            print('name;os;free disk space')

    def printFooter(self):
        """Print table if table format requested"""
        if (self.format == 'table'):
            print(self.table)

    def print(self, server):
        """Print the data of the specified server monitor"""

        name = server['name']
        os = server['os'] if 'os' in server else ''
        last_data = server['last_data']
        disk_info = ''
        if 'df' in last_data:
            for disk in last_data['df']:
                free_disk_space = disk['free_bytes']
                used_disk_space = disk['used_bytes']
                total_disk_space = free_disk_space + used_disk_space
                free_disk_space_percent = free_disk_space / total_disk_space * 100
                mount = disk['mount']

                # add separator
                if disk_info:
                    disk_info += ', '

                if free_disk_space_percent <= float(self.config.threshold_free_diskspace):
                    disk_info += f"{bcolors.FAIL}" + "{:.0f}".format(free_disk_space_percent) + "% free on " + mount + f"{bcolors.ENDC}"
                else:
                    disk_info += "{:.0f}".format(free_disk_space_percent) + "% free on " + mount

        if (self.format == 'table'):
            self.table.add_row([name, os, disk_info])

        elif (self.format == 'csv'):
            print(f"{name};{os};{disk_info}")

        else:
            print(json.dumps(server, indent=4))
