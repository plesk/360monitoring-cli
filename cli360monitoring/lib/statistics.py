#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .monitoringconfig import MonitoringConfig
from .servers import Servers
from .sites import Sites
from .contacts import Contacts
from .usertokens import UserTokens
from .functions import printError, printWarn
from .bcolors import bcolors

class Statistics(object):

    def __init__(self, config):
        self.config = config
        self.statistics = None
        self.format = 'table'

        self.table = PrettyTable()
        self.table.field_names = ['Value', 'Metric']
        self.table.align['Value'] = 'r'
        self.table.align['Metric'] = 'l'

    def print(self):
        """Iterate through all assets and print statistics"""

        self.printHeader()

        servers = Servers(self.config)
        if servers.fetchData():
            self.printAsset('Servers', len(servers.servers))

        sites = Sites(self.config)
        if sites.fetchData():
            sum_uptime = 0
            sum_ttfb = 0
            num_monitors = len(sites.monitors)
            self.printAsset('Sites', len(sites.monitors))

            for monitor in sites.monitors:
                uptime_percentage = float(monitor['uptime_percentage'])

                if 'last_check' in monitor and 'ttfb' in monitor['last_check']:
                    ttfb = float(monitor['last_check']['ttfb'])
                    sum_uptime = sum_uptime + uptime_percentage
                    sum_ttfb = sum_ttfb + ttfb

            avg_uptime = sum_uptime / num_monitors if sum_uptime > 0 and num_monitors > 0 else 0
            avg_ttfb = sum_ttfb / num_monitors if sum_ttfb > 0 and num_monitors > 0 else 0

            if avg_uptime <= float(self.config.threshold_uptime):
                uptime_percentage_text = f"{bcolors.FAIL}" + "{:.4f}".format(avg_uptime) + f"{bcolors.ENDC}"
            else:
                uptime_percentage_text = "{:.4f}".format(avg_uptime)

            if avg_ttfb >= float(self.config.threshold_ttfb):
                ttfb_text = f"{bcolors.FAIL}" + "{:.2f}".format(avg_ttfb) + f"{bcolors.ENDC}"
            else:
                ttfb_text = "{:.2f}".format(avg_ttfb)

            self.printAsset('% avg uptime of all sites', uptime_percentage_text)
            self.printAsset('sec avg ttfb of all sites', ttfb_text)

        contacts = Contacts(self.config)
        if contacts.fetchData():
            self.printAsset('Contacts', len(contacts.contacts))

        usertokens = UserTokens(self.config)
        if usertokens.fetchData():
            self.printAsset('User Tokens', len(usertokens.usertokens))

        self.printFooter()

    def printHeader(self):
        """Print CSV header if CSV format requested"""

        if (self.format == 'csv'):
            print('metric;value')

    def printFooter(self):
        """Print table if table format requested"""

        if (self.format == 'table'):
            print(self.table)

    def printAsset(self, asset: str, value):
        """Print the data of the specified web monitor"""

        if (self.format == 'table'):
            self.table.add_row([value, asset])

        elif (self.format == 'csv'):
            print(f"{asset};{value}")
