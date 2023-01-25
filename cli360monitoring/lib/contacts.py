#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .monitoringconfig import MonitoringConfig
from .functions import printError, printWarn

class Contacts(object):

    def __init__(self, config):
        self.config = config
        self.contacts = None
        self.format = 'table'
        self.table = PrettyTable()
        self.table.field_names = ['Name', 'Email', 'SMS', 'Method']
        self.table.align['Name'] = 'l'
        self.table.align['Email'] = 'l'
        self.table.align['SMS'] = 'l'
        self.table.align['Method'] = 'c'

    def fetchData(self):
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
            self.contacts = response.json()['contacts']
            return True
        else:
            printError("An error occurred:", response.status_code)
            self.contacts = None
            return False

    def list(self):
        """Iterate through list of contacts and print details"""

        if self.fetchData():
            self.printHeader()

            for contact in self.contacts:
                self.print(contact)

            self.printFooter()

    def get(self, pattern: str):
        """Print the data of all contacts that match the specified name pattern"""

        if pattern and self.fetchData():
            for contact in self.contacts:
                if pattern == contact['id'] or pattern in contact['name'] or pattern == contact['email']:
                    self.print(contact)

    def add(self, name: str, email: str, sms: str = ''):
        """Add a contact for the given name"""

        if name and self.fetchData():

            for contact in self.contacts:
                if contact['name'] == name:
                    print(name, "already exists and will not be added")
                    return

            # Make request to API endpoint
            data = {
                "name": name,
                "channels": {
                    "email": email,
                    "sms": sms
                }
            }
            response = requests.post(self.config.endpoint + "contacts",  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 200:
                print("Added contact:", name)
            else:
                printError("Failed to add contact", name, "with response code: ", response.status_code)

    def remove(self, pattern: str):
        """Remove the contact for the given name"""

        if pattern and self.fetchData():

            removed = 0
            for contact in self.contacts:
                id = contact['id']
                name = contact['name']
                email = contact['email'] if 'email' in contact else ''
                sms = contact['phonenumber'] if 'phonenumber' in contact else ''

                if pattern == id or pattern == name or pattern == email or pattern == sms:
                    print("Try to remove contact:", name, "[", id, "]")
                    removed += 1

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + "contact/" + id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print("Removed contact:", name, "[", id, "]")
                    else:
                        printError("Failed to remove contact", name, "[", id, "] with response code: ", response.status_code)

                    return

            if removed == 0:
                printWarn("Contact with id or name", pattern, "not found")

    def printHeader(self):
        """Print CSV header if CSV format requested"""
        if (self.format == 'csv'):
            print('name;email;sms;method')

    def printFooter(self):
        """Print table if table format requested"""
        if (self.format == 'table'):
            print(self.table)

    def print(self, contact):
        """Print the data of the specified contact"""

        name = contact['name']
        email = contact['email'] if 'email' in contact else ''
        sms = contact['phonenumber'] if 'phonenumber' in contact else ''
        method = contact['method'] if 'method' in contact else ''

        if (self.format == 'table'):
            self.table.add_row([name, email, sms, method])

        elif (self.format == 'csv'):
            print(f"{name};{email};{sms};{method}")

        else:
            print(json.dumps(contact, indent=4))
