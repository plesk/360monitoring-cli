#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .config import Config
from .functions import printError, printWarn
from .bcolors import bcolors

class Sites(object):

    def __init__(self, config):
        self.config = config
        self.monitors = None
        self.format = 'table'

        self.table = PrettyTable()
        self.table.field_names = ['ID', 'URL', 'Status', 'Uptime %', 'Time to first Byte', 'Location']
        self.table.align['ID'] = 'l'
        self.table.align['URL'] = 'l'
        self.table.align['Status'] = 'l'
        self.table.align['Uptime %'] = 'r'
        self.table.align['Time to first Byte'] = 'c'
        self.table.align['Location'] = 'c'

        self.sum_uptime = 0
        self.sum_ttfb = 0
        self.num_monitors = 0

    def fetchData(self):
        """Retrieve the list of all website monitors"""

        # if data is already downloaded, use cached data
        if self.monitors != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        if self.config.debug:
            print('GET', self.config.endpoint + 'monitors?', self.config.params())

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + 'monitors', params=self.config.params(), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of servers from response
            self.monitors = response.json()['monitors']
            return True
        else:
            printError('An error occurred:', response.status_code)
            self.monitors = None
            return False

    def list(self, id: str = '', url: str = '', name: str = '', location: str = '', pattern: str = '', issuesOnly: bool = False):
        """Iterate through list of web monitors and print details"""

        if self.fetchData():
            self.printHeader()

            for monitor in self.monitors:
                if (id or url or name or location or pattern):
                    if (id and monitor['id'] == id) \
                        or (url and monitor['url'] == url) \
                        or (name and 'name' in monitor and monitor['name'] == name) \
                        or (location and location in monitor['monitor']['name']) \
                        or (pattern and pattern in monitor['url']):
                        if (not issuesOnly) or self.hasIssue(monitor):
                            self.print(monitor)
                else:
                    if (not issuesOnly) or self.hasIssue(monitor):
                        self.print(monitor)

            self.printFooter()

    def add(self, url: str, protocol: str = 'https', name: str = '', force: bool = False):
        """Add a monitor for the given URL"""

        if url and self.fetchData():

            # urls do not include the protocol
            url = url.replace('https://', '').replace('http://', '')

            # use the url as name if not specified otherwise
            if not name:
                name = url

            # use https as protocol if not specified otherwise
            if not protocol:
                protocol = 'https'

            # check if monitored url already exists unless --force is specified
            if not force:
                for monitor in self.monitors:
                    if monitor['url'] == url:
                        print(url, 'already exists and will not be added')
                        return

            # other parameters:
            #   port: int (e.g. 443, 80)
            #   keyword: string that needs to be in the http response body (e.g. "error")
            #   redirects: int (e.g. 3 max redirects; 0 for no redirects)
            #   timeout: int (e.g. 30 seconds)

            # Make request to API endpoint
            data = {
                'url': url,
                'name': name,
                'protocol': protocol
            }

            if self.config.debug:
                print('POST', self.config.endpoint + 'monitors?', data)

            if self.config.readonly:
                return False

            response = requests.post(self.config.endpoint + 'monitors',  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 200:
                print('Added site monitor:', url)
                return True
            else:
                printError('Failed to add site monitor', url, 'with response code:', response.status_code)
                return False

        else:
            return False

    def remove(self, id: str = '', url: str = '', name: str = '', location: str = '', pattern: str = ''):
        """Remove the monitor for the given URL"""

        removed = 0
        if (id or url or name or location or pattern) and self.fetchData():
            for monitor in self.monitors:
                curr_id = monitor['id']
                curr_url = monitor['url']
                curr_name = monitor['name'] if 'name' in monitor else ''
                curr_location = monitor['monitor']['name']

                if (id == curr_id) \
                    or (url and url == curr_url) \
                    or (name and name == curr_name) \
                    or (location and location in curr_location) \
                    or (pattern and pattern in curr_url):
                    removed += 1

                    if self.config.debug:
                        print('DELETE', self.config.endpoint + 'monitor/' + curr_id)

                    if self.config.readonly:
                        return False

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + 'monitor/' + curr_id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print('Removed site monitor:', curr_url, '[', curr_id, ']')
                        return True
                    else:
                        printError('Failed to remove site monitor', curr_url, '[', curr_id, '] with response code:', response.status_code)
                        return False

        if removed == 0:
            printWarn('No monitors with given pattern found: id=' + id, 'url=', url, 'name=' + name, 'location=' + location, 'pattern=' + pattern)

    def hasIssue(self, monitor):
        """Return True if the specified monitor has some issue by having a value outside of the expected threshold specified in config file"""

        if float(monitor['uptime_percentage']) <= float(self.config.threshold_uptime):
            return True

        if 'last_check' in monitor and 'ttfb' in monitor['last_check']:
            if float(monitor['last_check']['ttfb']) >= float(self.config.threshold_ttfb):
                return True

        return False

    def printHeader(self):
        """Print CSV header if CSV format requested"""

        if (self.format == 'csv'):
            print('id;url;name;code;status;status_message;uptime_percentage;ttfb;location')

        self.sum_uptime = 0
        self.sum_ttfb = 0
        self.num_monitors = 0

    def printFooter(self):
        """Print table if table format requested"""

        if (self.format == 'table'):

            avg_uptime = self.sum_uptime / self.num_monitors if self.sum_uptime > 0 and self.num_monitors > 0 else 0
            avg_ttfb = self.sum_ttfb / self.num_monitors if self.sum_ttfb > 0 and self.num_monitors > 0 else 0

            if avg_uptime <= float(self.config.threshold_uptime):
                uptime_percentage_text = f"{bcolors.FAIL}" + "{:.4f}".format(avg_uptime) + f"{bcolors.ENDC}"
            else:
                uptime_percentage_text = "{:.4f}".format(avg_uptime)

            if avg_ttfb >= float(self.config.threshold_ttfb):
                ttfb_text = f"{bcolors.FAIL}" + "{:.2f}".format(avg_ttfb) + f"{bcolors.ENDC}"
            else:
                ttfb_text = "{:.2f}".format(avg_ttfb)

            # add average row as table footer
            self.table.add_row(['', 'Average of ' + str(self.num_monitors) + ' monitors', '', uptime_percentage_text, ttfb_text, ''])

            if self.config.hide_ids:
                self.table.del_column('ID')

            # Get string to be printed and create list of elements separated by \n
            list_of_table_lines = self.table.get_string().split('\n')

            # Use the first line (+---+-- ...) as horizontal rule to insert later
            horizontal_line = list_of_table_lines[0]

            # Print the table
            # Treat the last n lines as "result lines" that are seperated from the
            # rest of the table by the horizontal line
            result_lines = 1
            print("\n".join(list_of_table_lines[:-(result_lines + 1)]))
            print(horizontal_line)
            print("\n".join(list_of_table_lines[-(result_lines + 1):]))

    def print(self, monitor):
        """Print the data of the specified web monitor"""

        if (self.format == 'json'):
            print(json.dumps(monitor, indent=4))
            return

        id = monitor['id']
        url = monitor['url']
        name = monitor['name'] if 'name' in monitor else ''
        code = monitor['code'] if 'code' in monitor else ''
        status = monitor['status'] if 'status' in monitor else ''
        status_message = monitor['status_message'] if 'status_message' in monitor else ''
        location = monitor['monitor']['name']
        uptime_percentage = float(monitor['uptime_percentage'])

        if 'last_check' in monitor and 'ttfb' in monitor['last_check']:
            ttfb = float(monitor['last_check']['ttfb'])
            self.sum_uptime = self.sum_uptime + uptime_percentage
            self.sum_ttfb = self.sum_ttfb + ttfb
            self.num_monitors = self.num_monitors + 1
        else:
            ttfb = -1

        if (self.format == 'csv'):
            print(f"{id};{url};{name};{code};{status};{status_message};{uptime_percentage}%;{ttfb};{location}")
        else:
            if uptime_percentage <= float(self.config.threshold_uptime):
                uptime_percentage_text = f"{bcolors.FAIL}" + "{:.4f}".format(uptime_percentage) + f"{bcolors.ENDC}"
            else:
                uptime_percentage_text = "{:.4f}".format(uptime_percentage)

            if ttfb >= float(self.config.threshold_ttfb):
                ttfb_text = f"{bcolors.FAIL}" + "{:.2f}".format(ttfb) + f"{bcolors.ENDC}"
            elif ttfb != -1:
                ttfb_text = "{:.2f}".format(ttfb)
            else:
                ttfb_text = f"{bcolors.FAIL}n/a{bcolors.ENDC}"

            self.table.add_row([id, url, status_message, uptime_percentage_text, ttfb_text, location])
