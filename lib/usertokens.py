#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable
from lib.monitoringconfig import MonitoringConfig

class UserTokens(object):

    def __init__(self, config):
        self.config = config
        self.format = 'table'
        self.table = PrettyTable()
        self.table.field_names = ["Token"]
        self.usertokens = None

    def fetch_data(self):
        """Retrieve the list of all usertokens"""

        if self.usertokens != None:
            return True

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + "usertoken", params="perpage=" + str(self.config.max_items), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of usertokens from response
            json = response.json()
            if 'tokens' in json:
                self.usertokens = response.json()["tokens"]
                return True
            else:
                self.usertokens = None
                return False
        else:
            print("An error occurred:", response.status_code)
            self.usertokens = None
            return False

    def list(self):
        """Iterate through list of usertokens and print details"""

        self.fetch_data()
        self.print_header()

        if self.usertokens != None:
            for usertoken in self.usertokens:
                self.print(usertoken)

        self.print_footer()

    def get(self, pattern: str):
        """Print the data of all usertokens that match the specified pattern"""

        if pattern:
            self.fetch_data()

            for usertoken in self.usertokens:
                if pattern == usertoken["token"]:
                    self.print(usertoken)

    def token(self):
        """Print the data of first usertoken"""

        self.fetch_data()

        if len(self.usertokens) > 0:
            return self.usertokens[0]['token']

    def create(self):
        """Create a new usertoken"""

        response = requests.post(self.config.endpoint + "usertoken",  headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            print ("Created usertoken")
        else:
            print("Failed to create usertoken with response code: ", response.status_code)

    def print_header(self):
        """Print CSV header if CSV format requested"""
        if (self.format == 'csv'):
            print('token')

    def print_footer(self):
        """Print table if table format requested"""
        if (self.format == 'table'):
            print(self.table)

    def print(self, usertoken):
        """Print the data of the specified usertoken"""

        token = usertoken['token']

        if (self.format == 'table'):
            self.table.add_row([token])

        elif (self.format == 'csv'):
            print(f"{token}")

        else:
            print(json.dumps(usertoken, indent=4))
