#!/usr/bin/env python3

import json
from prettytable import PrettyTable

from .api import apiGet, apiPost, apiDelete
from .config import Config
from .functions import printError, printWarn

class Contacts(object):

    def __init__(self, config: Config):
        self.config = config
        self.contacts = None
        self.format = 'table'

        self.table = PrettyTable(field_names=['ID', 'Name', 'Email', 'Phone', 'Method'])
        self.table.align['ID'] = 'l'
        self.table.align['Name'] = 'l'
        self.table.align['Email'] = 'l'
        self.table.align['Phone'] = 'l'
        self.table.align['Method'] = 'c'

    def fetchData(self):
        """Retrieve the list of all contacts"""

        # if data is already downloaded, use cached data
        if self.contacts != None:
            return True

        response_json = apiGet('contacts', 200, self.config)
        if response_json:
            if 'contacts' in response_json:
                self.contacts = response_json['contacts']
                return True
            else:
                printWarn('No contacts found')
                self.contacts = None
                return False
        else:
            self.contacts = None
            return False

    def list(self, id: str = '', name: str = '', email: str = '', phone: str = '', sort: str = '', reverse: bool = False, limit: int = 0):
        """Iterate through list of contacts and print details"""

        if self.fetchData():
            # if JSON was requested and no filters, then just print it without iterating through
            if (self.format == 'json' and not (id or name or email or phone or limit > 0)):
                print(json.dumps(self.contacts, indent=4))
                return

            for contact in self.contacts:
                if (id or name or email or phone):
                    if (id and 'id' in contact and contact['id'] == id) \
                        or (name and 'name' in contact and contact['name'] == name) \
                        or (email and 'email' in contact and contact['email'] == email) \
                        or (phone and 'phonenumber' in contact and contact['phonenumber'] == phone):
                        self.print(contact)
                else:
                    self.print(contact)

            self.printFooter(sort=sort, reverse=reverse, limit=limit)

    def add(self, name: str, email: str = '', sms: str = ''):
        """Add a contact for the given name"""

        if name and self.fetchData():
            for contact in self.contacts:
                if contact['name'] == name:
                    print(name, 'already exists and will not be added')
                    return

            # Make request to API endpoint
            data = {
                'name': name,
                'channels': {
                    'email': email,
                    'sms': sms
                }
            }
            apiPost('contacts', self.config, data=data, expectedStatusCode=200, successMessage='Added contact \"' + name + '\"', errorMessage='Failed to add contact \"' + name + '\"')

    def remove(self, id: str = '', name: str = '', email: str = '', phone: str = ''):
        """Remove the contact for the given name"""

        if (id or name or email or phone) and self.fetchData():
            for contact in self.contacts:
                curr_id = contact['id']
                curr_name = contact['name']
                curr_email = contact['email'] if 'email' in contact else ''
                curr_phone = contact['phonenumber'] if 'phonenumber' in contact else ''

                if (id == curr_id) \
                    or (name and name == curr_name) \
                    or (email and email == curr_email) \
                    or (phone and phone == curr_phone):
                    apiDelete('contact/' + curr_id, self.config, expectedStatusCode=204, successMessage='Removed contact \"' + curr_name + '\" [' + curr_id + ']', errorMessage='Failed to remove contact \"' + curr_name + '\" [' + curr_id + ']')
                    return

        printWarn('No contact with given pattern found: id=' + id, 'name=' + name, 'email=' + email, 'phone=' + phone)

    def printFooter(self, sort: str = '', reverse: bool = False, limit: int = 0):
        """Print table if table format requested"""

        if (self.format == 'table'):
            if self.config.hide_ids:
                self.table.del_column('ID')

            if sort:
                # if sort contains the column index instead of the column name, get the column name instead
                if sort.isdecimal():
                    sort = self.table.get_csv_string().split(',')[int(sort) - 1]
            else:
                sort = None

            if limit > 0:
                print(self.table.get_string(sortby=sort, reversesort=reverse, start=0, end=limit))
            else:
                print(self.table.get_string(sortby=sort, reversesort=reverse))

        elif (self.format == 'csv'):
            print(self.table.get_csv_string(delimiter=self.config.delimiter))

    def print(self, contact):
        """Print the data of the specified contact"""

        if (self.format == 'json'):
            print(json.dumps(contact, indent=4))
            return

        id = contact['id']
        name = contact['name']
        email = contact['email'] if 'email' in contact else ''
        phone = contact['phonenumber'] if 'phonenumber' in contact else ''
        method = contact['method'] if 'method' in contact else ''

        self.table.add_row([id, name, email, phone, method])
