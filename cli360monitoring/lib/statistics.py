#!/usr/bin/env python3

from prettytable import PrettyTable

from .config import Config
from .servers import Servers
from .sites import Sites
from .contacts import Contacts
from .usertokens import UserTokens
from .bcolors import bcolors

class Statistics(object):

    def __init__(self, config: Config):
        self.config = config

        self.table = PrettyTable(field_names=['Value', 'Metric'])
        self.table.align['Value'] = 'r'
        self.table.align['Metric'] = 'l'

    def print(self, format: str = 'table'):
        """Iterate through all assets and print statistics"""

        servers = Servers(self.config)
        if servers.fetchData():
            sum_cpu_usage = 0
            sum_mem_usage = 0
            sum_disk_usage = 0
            num_servers = len(servers.servers)
            self.table.add_row([len(servers.servers), 'Servers'])

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

            self.table.add_row([avg_cpu_usage_text, '% avg cpu usage of all ' + str(num_servers) + ' servers'])
            self.table.add_row([avg_mem_usage_text, '% avg mem usage of all ' + str(num_servers) + ' servers'])
            self.table.add_row([avg_disk_usage_text, '% avg disk usage of all ' + str(num_servers) + ' servers'])

        sites = Sites(self.config)
        if sites.fetchData():
            sum_uptime = 0
            sum_ttfb = 0
            num_monitors = len(sites.monitors)
            self.table.add_row([len(sites.monitors), 'Sites'])

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

            self.table.add_row([uptime_percentage_text, '% avg uptime of all ' + str(num_monitors) + ' sites'])
            self.table.add_row([ttfb_text, 'sec avg ttfb of all ' + str(num_monitors) + ' sites'])

        contacts = Contacts(self.config)
        if contacts.fetchData():
            self.table.add_row([len(contacts.contacts), 'Contacts'])

        usertokens = UserTokens(self.config)
        if usertokens.fetchData():
            self.table.add_row([len(usertokens.usertokens), 'User Tokens'])

        if (format == 'table'):
            print(self.table)
        elif (format == 'csv'):
            print(self.table.get_csv_string(delimiter=self.config.delimiter))
