#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .config import Config
from .functions import printError, printWarn

class Contacts(object):

    def __init__(self, config):
        self.config = config
        self.contacts = None
        self.format = 'table'

        self.table = PrettyTable()
        self.table.field_names = ['ID', 'Name', 'Email', 'Phone', 'Method']
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

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        if self.config.debug:
            print('GET', self.config.endpoint + 'contacts?', self.config.params())

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + 'contacts', params=self.config.params(), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of contacts from response
            self.contacts = response.json()['contacts']
            return True
        else:
            printError('An error occurred:', response.status_code)
            self.contacts = None
            return False

    def list(self, id: str = '', name: str = '', email: str = '', phone: str = '', sort: str = '', reverse: bool = False, limit: int = 0, delimiter: str = ';'):
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

            self.printFooter(sort=sort, reverse=reverse, limit=limit, delimiter=delimiter)

    def add(self, name: str, email: str = '', sms: str = ''):
        """Add a contact for the given name"""

        if name and self.fetchData():

            for contact in self.contacts:
                if contact['name'] == name:
                    print(name, 'already exists and will not be added')
                    return False

            # Make request to API endpoint
            data = {
                'name': name,
                'channels': {
                    'email': email,
                    'sms': sms
                }
            }

            if self.config.debug:
                print('POST', self.config.endpoint + 'contacts?', data)

            if self.config.readonly:
                return False

            response = requests.post(self.config.endpoint + 'contacts',  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 200:
                print('Added contact:', name)
                return True
            else:
                printError('Failed to add contact', name, 'with response code:', response.status_code)
                return False

        else:
            return False

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

                    if self.config.debug:
                        print('DELETE', self.config.endpoint + 'contacts/' + curr_id)

                    if self.config.readonly:
                        return False

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + 'contact/' + curr_id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print('Removed contact:', curr_name, '[', curr_id, ']')
                        return True
                    else:
                        printError('Failed to remove contact', curr_name, '[', curr_id, '] with response code:', response.status_code)
                        return False

        printWarn('No contact with given pattern found: id=' + id, 'name=' + name, 'email=' + email, 'phone=' + phone)

    def printFooter(self, sort: str = '', reverse: bool = False, limit: int = 0, delimiter: str = ';'):
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
            print(self.table.get_csv_string(delimiter=delimiter))

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
