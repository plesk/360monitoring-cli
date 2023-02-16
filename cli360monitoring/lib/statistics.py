#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .config import Config
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
            sum_cpu_usage = 0
            sum_mem_usage = 0
            sum_disk_usage = 0
            num_servers = len(servers.servers)
            self.printAsset('Servers', len(servers.servers))

            for server in servers.servers:
                sum_cpu_usage = sum_cpu_usage + server['summary']['cpu_usage_percent'] if 'summary' in server else 0
                sum_mem_usage = sum_mem_usage + server['summary']['mem_usage_percent'] if 'summary' in server else 0
                sum_disk_usage = sum_disk_usage + server['summary']['disk_usage_percent'] if 'summary' in server else 0

            avg_cpu_usage = sum_cpu_usage / num_servers if sum_cpu_usage > 0 and num_servers > 0 else 0
            avg_mem_usage = sum_mem_usage / num_servers if sum_mem_usage > 0 and num_servers > 0 else 0
            avg_disk_usage = sum_disk_usage / num_servers if sum_disk_usage > 0 and num_servers > 0 else 0

            if avg_cpu_usage >= float(self.config.threshold_cpu_usage):
                avg_cpu_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_cpu_usage) + f"{bcolors.ENDC}"
            else:
               avg_cpu_usage_text = "{:.1f}".format(avg_cpu_usage)

            if avg_mem_usage >= float(self.config.threshold_mem_usage):
                avg_mem_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_mem_usage) + f"{bcolors.ENDC}"
            else:
               avg_mem_usage_text = "{:.1f}".format(avg_mem_usage)

            if avg_disk_usage >= float(self.config.threshold_disk_usage):
                avg_disk_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_disk_usage) + f"{bcolors.ENDC}"
            else:
               avg_disk_usage_text = "{:.1f}".format(avg_disk_usage)

            self.printAsset('% avg cpu usage of all ' + str(num_servers) + ' servers', avg_cpu_usage_text)
            self.printAsset('% avg mem usage of all ' + str(num_servers) + ' servers', avg_mem_usage_text)
            self.printAsset('% avg disk usage of all ' + str(num_servers) + ' servers', avg_disk_usage_text)

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

            self.printAsset('% avg uptime of all ' + str(num_monitors) + ' sites', uptime_percentage_text)
            self.printAsset('sec avg ttfb of all ' + str(num_monitors) + ' sites', ttfb_text)

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

        if (self.format == 'csv'):
            print(f"{asset};{value}")
        else:
            self.table.add_row([value, asset])
