#!/usr/bin/env python3

import json
from prettytable import PrettyTable

from .api import apiGet, apiPut
from .config import Config
from .functions import printError, printWarn
from .bcolors import bcolors

class Servers(object):

    def __init__(self, config: Config):
        self.config = config
        self.servers = None
        self.format = 'table'

        self.table = PrettyTable(field_names=['ID', 'Server name', 'IP Address', 'Status', 'OS', 'CPU Usage %', 'Mem Usage %', 'Disk Usage %', 'Disk Info', 'Tags'])
        self.table.align['ID'] = 'l'
        self.table.align['Server name'] = 'l'
        self.table.min_width['Server name'] = 24
        self.table.align['Tags'] = 'l'

        self.sum_cpu_usage = 0
        self.sum_mem_usage = 0
        self.sum_disk_usage = 0
        self.num_servers = 0

    def fetchData(self, tags: str = ''):
        """Retrieve a list of all monitored servers"""

        # if data is already downloaded, use cached data
        if self.servers != None:
            return True

        response_json = apiGet('servers', 200, self.config, self.config.params(tags))
        if response_json:
            if 'servers' in response_json:
                self.servers = response_json['servers']
                return True
            else:
                printWarn('No servers found for tags', tags)
                self.servers = None
                return False
        else:
            self.servers = None
            return False

    def update(self, serverId: str, tags):
        """Update a specific server and add specified tags to it"""

        data = {
            "tags": tags
        }
        apiPut('server/' + serverId, self.config, data=data, expectedStatusCode=200, successMessage='Updated tags of server ' + serverId + ' to ' + tags, errorMessage='Failed to update server ' + serverId)

    def list(self, issuesOnly: bool, sort: str, reverse: bool, limit: int, tags):
        """Iterate through list of server monitors and print details"""

        if self.fetchData(','.join(tags)):

            # if JSON was requested and no filters, then just print it without iterating through
            if (self.format == 'json' and not (issuesOnly or len(tags) > 0 or limit > 0)):
                print(json.dumps(self.servers, indent=4))
                return

            self.printHeader()

            self.sum_cpu_usage = 0
            self.sum_mem_usage = 0
            self.sum_disk_usage = 0
            self.num_servers = 0

            # Iterate through list of servers and print data, etc.
            for server in self.servers:
                if len(tags) == 0:
                    if (not issuesOnly) or self.hasIssue(server):
                        self.print(server)
                elif 'tags' in server:
                    match = True
                    for tag in tags:
                        if not tag in server['tags']:
                            match = False
                            break
                    if match:
                        if (not issuesOnly) or self.hasIssue(server):
                            self.print(server)

            self.printFooter(sort=sort, reverse=reverse, limit=limit)

    def setTags(self, pattern: str, tags):
        """Set the tags for the server specified with pattern. Pattern can be either the server ID or its name"""

        if pattern and len(tags) > 0 and self.fetchData():
            for server in self.servers:
                if pattern == server['id'] or pattern in server['name']:
                    return self.update(server['id'], tags)

        printWarn('No server with given pattern found: ' + pattern)

    def getServerId(self, name: str):
        """Return Server Id for the server with the specified name. Only the first matching entry (exact match) is returned or empty string if not found"""

        if name and self.fetchData():
            # Iterate through list of servers and find the specified one
            for server in self.servers:
                if server['name'] == name:
                    return server['id']

        return ''

    def getRecommendation(self, server):
        """Return recommendation text if the specified server has some issue by having a value outside of the expected threshold specified in config file"""

        last_data = server['last_data']

        mem_usage_percent = server['summary']['mem_usage_percent'] if 'summary' in server else 0
        memory_total = last_data['memory']['total'] if 'memory' in last_data else 0
        if memory_total > 0 and mem_usage_percent >= float(self.config.threshold_mem_usage):
            memory_total_gb = memory_total / 1024 / 1024
            memory_total_gb_recommended = round(memory_total_gb * 2)
            if (memory_total_gb_recommended % 2) != 0:
                memory_total_gb_recommended += 1
            return 'Memory is too small for your workload. Please consider upgrading to a larger server with at least ' + str(memory_total_gb_recommended) + ' GB memory.'

        cpu_usage_percent = server['summary']['cpu_usage_percent'] if 'summary' in server else 0
        cores = last_data['cores'] if 'cores' in last_data else 0
        if cores > 0 and cpu_usage_percent >= float(self.config.threshold_cpu_usage):
            cores_recommended = round(cores * 2)
            if (cores % 2) != 0:
                cores += 1
            return 'CPU is too small for your workload. Please consider upgrading to a larger server with at least ' + str(cores_recommended) + ' CPU cores.'

        disk_usage_percent = server['summary']['disk_usage_percent'] if 'summary' in server else 0
        last_data = server['last_data']
        if 'df' in last_data:  # disk_usage_percent >= float(self.config.threshold_disk_usage)
            for disk in last_data['df']:
                mount = disk['mount']
                free_disk_space = disk['free_bytes']
                used_disk_space = disk['used_bytes']
                total_disk_space = free_disk_space + used_disk_space
                free_disk_space_percent = free_disk_space / total_disk_space * 100
                total_disk_space_gb = total_disk_space / 1024 / 1024
                total_disk_space_gb_recommended = round(total_disk_space_gb * 2)
                if (total_disk_space_gb_recommended % 2) != 0:
                    total_disk_space_gb_recommended += 1

                if free_disk_space_percent <= float(self.config.threshold_free_diskspace):
                    return 'Disk volume "' + mount + '" is almost exhausted. Please consider extending your storage volume or upgrading to a larger server with at least ' + str(total_disk_space_gb_recommended) + ' GB disk space for this volume.'

        return ''

    def hasIssue(self, server):
        """Return True if the specified server has some issue by having a value outside of the expected threshold specified in config file"""
        if self.getRecommendation(server):
            return True
        else:
            return False

    def printHeader(self):
        """Print CSV if CSV format requested"""
        if (self.format == 'csv'):
            print(self.config.delimiter.join(self.table.field_names))

    def printFooter(self, sort: str = '', reverse: bool = False, limit: int = 0):
        """Print table if table format requested"""

        if (self.format == 'table'):

            avg_cpu_usage = self.sum_cpu_usage / self.num_servers if self.sum_cpu_usage > 0 and self.num_servers > 0 else 0
            avg_mem_usage = self.sum_mem_usage / self.num_servers if self.sum_mem_usage > 0 and self.num_servers > 0 else 0
            avg_disk_usage = self.sum_disk_usage / self.num_servers if self.sum_disk_usage > 0 and self.num_servers > 0 else 0

            if avg_cpu_usage >= float(self.config.threshold_cpu_usage):
                avg_cpu_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_cpu_usage) + '%' + f"{bcolors.ENDC}"
            else:
               avg_cpu_usage_text = "{:.1f}".format(avg_cpu_usage) + '%'

            if avg_mem_usage >= float(self.config.threshold_mem_usage):
                avg_mem_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_mem_usage) + '%' + f"{bcolors.ENDC}"
            else:
               avg_mem_usage_text = "{:.1f}".format(avg_mem_usage) + '%'

            if avg_disk_usage >= float(self.config.threshold_disk_usage):
                avg_disk_usage_text = f"{bcolors.FAIL}" + "{:.1f}".format(avg_disk_usage) + '%' + f"{bcolors.ENDC}"
            else:
               avg_disk_usage_text = "{:.1f}".format(avg_disk_usage) + '%'

            # add average row as table footer
            self.table.add_row(['', 'Average of ' + str(self.num_servers) + ' servers', '', '', '', avg_cpu_usage_text, avg_mem_usage_text, avg_disk_usage_text, '', ''])

            if self.config.hide_ids:
                self.table.del_column('ID')

            # Get string to be printed and create list of elements separated by \n
            list_of_table_lines = self.table.get_string().split('\n')

            # remember summary row
            summary_line = list_of_table_lines[-2]

            # remove summary row again to allow sorting and limiting
            self.table.del_row(len(self.table.rows)-1)

            if sort:
                # if sort contains the column index instead of the column name, get the column name instead
                if sort.isdecimal():
                    sort = self.table.get_csv_string().split(',')[int(sort) - 1]
            else:
                sort = None

            if limit > 0:
                list_of_table_lines = self.table.get_string(sortby=sort, reversesort=reverse, start=0, end=limit).split('\n')
            else:
                list_of_table_lines = self.table.get_string(sortby=sort, reversesort=reverse).split('\n')

            # Sorting by multiple columns could be done like this
            # list_of_table_lines = self.table.get_string(sortby=("Col Name 1", "Col Name 2")), reversesort=reverse).split('\n')

            # Print the table
            print('\n'.join(list_of_table_lines))
            print(summary_line)
            print(list_of_table_lines[0])

    def print(self, server):
        """Print the data of the specified server monitor"""

        if (self.format == 'json'):
            print(json.dumps(server, indent=4))
            return

        id = server['id']
        name = server['name']
        os = server['os'] if 'os' in server else ''
        agent_version = server['agent_version'] if 'agent_version' in server else ''
        status = server['status'] if 'status' in server else ''
        last_data = server['last_data']
        uptime_seconds = last_data['uptime']['seconds'] if 'uptime' in last_data else 0
        cores = last_data['cores'] if 'cores' in last_data else 0
        memory_used = last_data['memory']['used'] if 'memory' in last_data else 0
        memory_free = last_data['memory']['free'] if 'memory' in last_data else 0
        memory_available = last_data['memory']['available'] if 'memory' in last_data else 0
        memory_total = last_data['memory']['total'] if 'memory' in last_data else 0
        connecting_ip = server['connecting_ip'] if 'connecting_ip' in server else ''
        if 'ip_whois' in server and server['ip_whois']:
            ip_whois = server['ip_whois']
            ip_address = ip_whois['ip'] if 'ip' in ip_whois else ''
            ip_country = ip_whois['country'] if 'country' in ip_whois else ''
            ip_hoster = ip_whois['org'] if 'org' in ip_whois else ''
        else:
            ip_address = ''
            ip_country = ''
            ip_hoster = ''
        cpu_usage_percent = server['summary']['cpu_usage_percent'] if 'summary' in server else 0
        mem_usage_percent = server['summary']['mem_usage_percent'] if 'summary' in server else 0
        disk_usage_percent = server['summary']['disk_usage_percent'] if 'summary' in server else 0

        self.sum_cpu_usage = self.sum_cpu_usage + cpu_usage_percent
        self.sum_mem_usage = self.sum_mem_usage + mem_usage_percent
        self.sum_disk_usage = self.sum_disk_usage + disk_usage_percent
        self.num_servers = self.num_servers + 1

        if cpu_usage_percent >= float(self.config.threshold_cpu_usage):
            cpu_usage_percent_text = f"{bcolors.FAIL}" + "{:.1f}".format(cpu_usage_percent) + '%' + f"{bcolors.ENDC}"
        else:
            cpu_usage_percent_text = "{:.1f}".format(cpu_usage_percent) + '%'

        if mem_usage_percent >= float(self.config.threshold_mem_usage):
            mem_usage_percent_text = f"{bcolors.FAIL}" + "{:.1f}".format(mem_usage_percent) + '%' + f"{bcolors.ENDC}"
        else:
            mem_usage_percent_text = "{:.1f}".format(mem_usage_percent) + '%'

        if disk_usage_percent >= float(self.config.threshold_disk_usage):
            disk_usage_percent_text = f"{bcolors.FAIL}" + "{:.1f}".format(disk_usage_percent) + '%' + f"{bcolors.ENDC}"
        else:
            disk_usage_percent_text = "{:.1f}".format(disk_usage_percent) + '%'

        tags = ''
        if 'tags' in server and server['tags']:
            for tag in server['tags']:
                if tags:
                    tags += ', ' + tag
                else:
                    tags = tag

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

        if (self.format == 'csv'):
            print(self.config.delimiter.join([id, name, ip_address, status, os, str(cpu_usage_percent) + '%', str(mem_usage_percent) + '%', str(disk_usage_percent) + '%', disk_info, tags]))
        else:
            self.table.add_row([id, name, ip_address, status, os, cpu_usage_percent_text, mem_usage_percent_text, disk_usage_percent_text, disk_info, tags])
