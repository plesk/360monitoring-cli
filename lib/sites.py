#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable
from lib.monitoringconfig import MonitoringConfig

class Sites(object):

    def __init__(self, config):
        self.config = config
        self.format = 'table'
        self.table = PrettyTable()
        self.table.field_names = ["URL", "Uptime in %", "Time to first Byte", "Location"]
        self.monitors = None

    def fetch_data(self):
        """Retrieve the list of all website monitors"""

        if self.monitors != None:
            return True

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + "monitors", params="perpage=" + str(self.config.max_items), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of servers from response
            self.monitors = response.json()["monitors"]
            return True
        else:
            print("An error occurred:", response.status_code)
            self.monitors = None
            return False

    def list(self):
        """Iterate through list of web monitors and print details"""

        self.fetch_data()
        self.print_header()

        for monitor in self.monitors:
            self.print(monitor)

        self.print_footer()

    def get(self, pattern: str):
        """Print the data of all web monitors that match the specified url pattern"""

        if pattern:
            self.fetch_data()

            for monitor in self.monitors:
                if pattern == monitor["id"] or pattern in monitor["url"]:
                    self.print(monitor)

    def add(self, url: str):
        """Add a monitor for the given URL"""

        if url:
            self.fetch_data()

            for monitor in self.monitors:
                if monitor["url"] == url:
                    print (url, "already exists and will not be added")
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
                print ("Added site monitor:", url)
            else:
                print("Failed to add site monitor", url, "with response code: ", response.status_code)

    def remove(self, pattern: str):
        """Remove the monitor for the given URL"""

        if pattern:
            self.fetch_data()

            removed = 0
            for monitor in self.monitors:
                id = monitor["id"]
                url = monitor["url"]
                if pattern == id or pattern == url:
                    print ("Try to remove site monitor:", url, "[", id, "]")
                    removed += 1

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + "monitor/" + id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print ("Removed site monitor:", url, "[", id, "]")
                    else:
                        print ("Failed to remove site monitor", url, "[", id, "] with response code: ", response.status_code)

                    return

            if removed == 0:
                print ("Monitor with id or url", pattern, "not found")

    def print_header(self):
        """Print CSV header if CSV format requested"""
        if (self.format == 'csv'):
            print('url;uptime_percentage;ttfb;location')

    def print_footer(self):
        """Print table if table format requested"""
        if (self.format == 'table'):
            print(self.table)

    def print(self, monitor):
        """Print the data of the specified web monitor"""

        url = monitor["url"]
        location = monitor["monitor"]["name"]
        uptime_percentage = monitor["uptime_percentage"]
        ttfb = monitor["last_check"]["ttfb"]

        if (self.format == 'table'):
            self.table.add_row([url, "{:.2f}".format(uptime_percentage), "{:.2f}".format(ttfb), location])

        elif (self.format == 'csv'):
            print(f"{url};{uptime_percentage}%;{ttfb};{location}")

        else:
            print(json.dumps(monitor, indent=4))
