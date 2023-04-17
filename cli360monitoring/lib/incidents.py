#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from prettytable import PrettyTable

from .config import Config
from .functions import printError, printWarn

class Incidents(object):

    def __init__(self, config):
        self.config = config
        self.incidents = None
        self.format = 'table'

        self.table = PrettyTable()
        self.table.field_names = ['ID', 'Name', 'Body', 'Status', 'Timestamp']
        self.table.align['ID'] = 'l'
        self.table.align['Name'] = 'l'
        self.table.align['Body'] = 'l'
        self.table.align['Status'] = 'c'
        self.table.align['Timestamp'] = 'c'

    def fetchData(self, page_id: str):
        """Retrieve the list of all incidents"""

        # if data is already downloaded, use cached data
        if self.incidents != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        if self.config.debug:
            print('GET', self.config.endpoint + 'page/' + page_id + '/incidents', self.config.params())

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + 'page/' + page_id + '/incidents', params=self.config.params(), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of incidents from response
            response_json = response.json()
            if 'incidents' in response_json:
                self.incidents = response_json['incidents']
                return True
            else:
                printWarn('No incidents found for page', page_id)
                self.incidents = None
                return False
        else:
            printError('An error occurred:', response.status_code)
            self.incidents = None
            return False

    def list(self, page_id: str, id: str = '', name: str = ''):
        """Iterate through list of incidents and print details"""

        if self.fetchData(page_id):

            # if JSON was requested and no filters, then just print it without iterating through
            if (self.format == 'json'):
                print(json.dumps(self.incidents, indent=4))
                return

        for incident in self.incidents:
            if id or name:
                if (id and 'id' in incident and incident['id'] == id) \
                    or (name and 'name' in incident and incident['name'] == name):
                    self.print(incident)
            else:
                self.print(incident)

        self.printFooter()

    def add(self, page_id: str, name: str, body: str = ''):
        """Add a incident for the given name"""

        if page_id and name:

            if self.fetchData(page_id) and self.incidents:
                for incident in self.incidents:
                    if incident['name'] == name and incident['body'] == body:
                        print('Incident \'' + name + '\' already exists with this text and will not be added')
                        return False

            # Make request to API endpoint
            data = {
                'name': name,
                'body': body
            }

            if self.config.debug:
                print('POST', self.config.endpoint + 'page/' + page_id + '/incidents', data)

            if self.config.readonly:
                return False

            response = requests.post(self.config.endpoint + 'page/' + page_id + '/incidents',  data=json.dumps(data), headers=self.config.headers())

            # Check status code of response
            if response.status_code == 204:
                print('Added incident:', name)
                return True
            else:
                printError('Failed to add incident', name, 'to page', page_id, 'with response code:', response.status_code)
                return False

        else:
            return False

    def remove(self, page_id: str, id: str = '', name: str = ''):
        """Remove the incident for the given name"""

        if (id or name) and self.fetchData(page_id):
            for incident in self.incidents:
                curr_id = incident['id']
                curr_name = incident['name']
                curr_update_id = ''

                if (id and id == curr_id) \
                    or (name and name == curr_name):

                    if self.config.debug:
                        print('DELETE', self.config.endpoint + 'page/' + page_id + '/incident/' + curr_id + '/' + curr_update_id)

                    if self.config.readonly:
                        return False

                    # Make request to API endpoint
                    response = requests.delete(self.config.endpoint + 'page/' + page_id + '/incident/' + curr_id + '/' + curr_update_id, headers=self.config.headers())

                    # Check status code of response
                    if response.status_code == 204:
                        print('Removed incident:', curr_name, '[', curr_id, ']')
                        return True
                    else:
                        printError('Failed to remove incident', curr_name, '[', curr_id, '] from page \'' + page_id + '\' with response code:', response.status_code)
                        return False

        printWarn('No incident with given pattern found on page \'' + page_id + '\': id=' + id, 'name=' + name)

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

    def print(self, incident):
        """Print the data of the specified incident"""

        if (self.format == 'json'):
            print(json.dumps(incident, indent=4))
            return

        id = incident['id']
        name = incident['name'] if 'name' in incident else ''
        body = incident['body'] if 'body' in incident else ''
        status = incident['status'] if 'status' in incident else ''
        timestamp = datetime.fromtimestamp(incident['timestamp']) if 'timestamp' in incident else ''

        self.table.add_row([id, name, body, status, timestamp])
