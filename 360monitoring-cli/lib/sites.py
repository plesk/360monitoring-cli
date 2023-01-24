#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable
from lib.monitoringconfig import MonitoringConfig
from lib.functions import *

class Sites(object):

    def __init__(self, config):
        self.config = config
        self.monitors = None
        self.format = 'table'

        self.table = PrettyTable()
        self.table.field_names = ['URL', 'Uptime %', 'Time to first Byte', 'Location']
        self.table.align['URL'] = 'l'
        self.table.align['Uptime %'] = 'r'
        self.table.align['Time to first Byte'] = 'c'
        self.table.align['Location'] = 'c'

        self.sum_uptime = 0
        self.sum_ttfb = 0
        self.num_monitors = 0

    def fetch_data(self):
        """Retrieve the list of all website monitors"""

        # if data is already downloaded, use cached data
        if self.monitors != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + "monitors", params="perpage=" + str(self.config.max_items), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of servers from response
            self.monitors = response.json()["monitors"]
            return True
        else:
            print_error("An error occurred:", response.status_code)
            self.monitors = None
            return False

    def list(self):
        """Iterate through list of web monitors and print details"""

        if self.fetch_data():
            self.print_header()

            for monitor in self.monitors:
                self.print(monitor)

            self.print_footer()

    def get(self, pattern: str):
        """Print the data of all web monitors that match the specified url pattern"""

        if pattern and self.fetch_data():
            for monitor in self.monitors:
                if pattern == monitor["id"] or pattern in monitor["url"]:
                    self.print(monitor)

    def add(self, url: str):
        """Add a monitor for the given URL"""

        if url and self.fetch_data():

            for monitor in self.monitors:
                if monitor["url"] == url:
                    print(url, "already exists and will not be added")
                    return

            name = url.replace('https://', "").replace('http://', "")

            if not 'http' in url:
                url = 'https://' + url

            # Make request to API endpoint
            data = {
                "url": url,
                "name": name,
                "protocol": "https"
            }
            response = requests.post(self.config.endpoint + "monitors",  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 200:
                print("Added site monitor:", url)
            else:
                print_error("Failed to add site monitor", url, "with response code: ", response.status_code)

    def remove(self, pattern: str):
        """Remove the monitor for the given URL"""

        if pattern and self.fetch_data():

            removed = 0
            for monitor in self.monitors:
                id = monitor["id"]
                url = monitor["url"]
                if pattern == id or pattern == url:
                    print("Try to remove site monitor:", url, "[", id, "]")
                    removed += 1

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + "monitor/" + id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print("Removed site monitor:", url, "[", id, "]")
                    else:
                        print_error("Failed to remove site monitor", url, "[", id, "] with response code: ", response.status_code)

                    return

            if removed == 0:
                print_warn("Monitor with id or url", pattern, "not found")

    def print_header(self):
        """Print CSV header if CSV format requested"""
        if (self.format == 'csv'):
            print('url;uptime_percentage;ttfb;location')

        self.sum_uptime = 0
        self.sum_ttfb = 0
        self.num_monitors = 0

    def print_footer(self):
        """Print table if table format requested"""
        if (self.format == 'table'):

            avg_uptime = self.sum_uptime / self.num_monitors
            avg_ttfb = self.sum_ttfb / self.num_monitors

            if avg_uptime <= float(self.config.threshold_uptime):
                uptime_percentage_text = f"{bcolors.FAIL}" + "{:.4f}".format(avg_uptime) + f"{bcolors.ENDC}"
            else:
                uptime_percentage_text = "{:.4f}".format(avg_uptime)

            if avg_ttfb >= float(self.config.threshold_ttfb):
                ttfb_text = f"{bcolors.FAIL}" + "{:.2f}".format(avg_ttfb) + f"{bcolors.ENDC}"
            else:
                ttfb_text = "{:.2f}".format(avg_ttfb)

            # add average row as table footer
            self.table.add_row(['Average of ' + str(self.num_monitors) + ' monitors', uptime_percentage_text, ttfb_text, ''])

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

        url = monitor["url"]
        location = monitor["monitor"]["name"]
        uptime_percentage = float(monitor["uptime_percentage"])
        ttfb = float(monitor["last_check"]["ttfb"])

        self.sum_uptime = self.sum_uptime + uptime_percentage
        self.sum_ttfb = self.sum_ttfb + ttfb
        self.num_monitors = self.num_monitors + 1

        if (self.format == 'table'):

            if uptime_percentage <= float(self.config.threshold_uptime):
                uptime_percentage_text = f"{bcolors.FAIL}" + "{:.4f}".format(uptime_percentage) + f"{bcolors.ENDC}"
            else:
                uptime_percentage_text = "{:.4f}".format(uptime_percentage)

            if ttfb >= float(self.config.threshold_ttfb):
                ttfb_text = f"{bcolors.FAIL}" + "{:.2f}".format(ttfb) + f"{bcolors.ENDC}"
            else:
                ttfb_text = "{:.2f}".format(ttfb)

            self.table.add_row([url, uptime_percentage_text, ttfb_text, location])

        elif (self.format == 'csv'):
            print(f"{url};{uptime_percentage}%;{ttfb};{location}")

        else:
            print(json.dumps(monitor, indent=4))
