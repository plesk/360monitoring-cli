#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable
from lib.monitoringconfig import MonitoringConfig
from lib.functions import *

class Contacts(object):

    def __init__(self, config):
        self.config = config
        self.format = 'table'
        self.table = PrettyTable()
        self.table.field_names = ["Name", "Email", "Method"]
        self.contacts = None

    def fetch_data(self):
        """Retrieve the list of all contacts"""

        # if data is already downloaded, use cached data
        if self.contacts != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + "contacts", params="perpage=" + str(self.config.max_items), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of contacts from response
            self.contacts = response.json()["contacts"]
            return True
        else:
            print_error("An error occurred:", response.status_code)
            self.contacts = None
            return False

    def list(self):
        """Iterate through list of contacts and print details"""

        if self.fetch_data():
            self.print_header()

            for contact in self.contacts:
                self.print(contact)

            self.print_footer()

    def get(self, pattern: str):
        """Print the data of all contacts that match the specified name pattern"""

        if pattern and self.fetch_data():
            for contact in self.contacts:
                if pattern == contact["id"] or pattern in contact["name"] or pattern == contact["email"]:
                    self.print(contact)

    def add(self, name: str, email: str):
        """Add a contact for the given name"""

        if name and self.fetch_data():

            for contact in self.contacts:
                if contact["name"] == name:
                    print(name, "already exists and will not be added")
                    return

            # Make request to API endpoint
            data = {
                "name": name,
                "email": email
            }
            response = requests.post(self.config.endpoint + "contacts",  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 200:
                print("Added contact:", name)
            else:
                print_error("Failed to add contact", name, "with response code: ", response.status_code)

    def remove(self, pattern: str):
        """Remove the contact for the given name"""

        if pattern and self.fetch_data():

            removed = 0
            for contact in self.contacts:
                id = contact["id"]
                name = contact["name"]
                if pattern == id or pattern == name:
                    print("Try to remove contact:", name, "[", id, "]")
                    removed += 1

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + "contact/" + id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print("Removed contact:", name, "[", id, "]")
                    else:
                        print_error("Failed to remove contact", name, "[", id, "] with response code: ", response.status_code)

                    return

            if removed == 0:
                print_warn("Contact with id or name", pattern, "not found")

    def print_header(self):
        """Print CSV header if CSV format requested"""
        if (self.format == 'csv'):
            print('name;email;method')

    def print_footer(self):
        """Print table if table format requested"""
        if (self.format == 'table'):
            print(self.table)

    def print(self, contact):
        """Print the data of the specified contact"""

        name = contact['name']
        if 'email' in contact:
            email = contact['email']
        else:
            email = ''

        if 'method' in contact:
            method = contact['method']
        else:
            method = ''

        if (self.format == 'table'):
            self.table.add_row([name, email, method])

        elif (self.format == 'csv'):
            print(f"{name};{email};{method}")

        else:
            print(json.dumps(contact, indent=4))
