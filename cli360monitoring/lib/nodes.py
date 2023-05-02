#!/usr/bin/env python3

import json
from prettytable import PrettyTable

from .api import apiGet
from .config import Config
from .functions import printError, printWarn

class Nodes(object):

    def __init__(self, config: Config, format: str = 'table'):
        self.config = config
        self.format = format
        self.nodes = None

        self.table = PrettyTable(field_names=['ID', 'Name'])
        self.table.align['ID'] = 'l'
        self.table.align['Name'] = 'l'

    def fetchData(self):
        """Retrieve the list of all nodes"""

        # if data is already downloaded, use cached data
        if self.nodes != None:
            return True

        response_json = apiGet('nodes', 200, self.config)
        if response_json:
            if 'nodes' in response_json:
                self.nodes = response_json['nodes']
                return True
            else:
                printWarn('No nodes found')
                self.nodes = None
                return False
        else:
            self.nodes = None
            return False

    def list(self, id: str = '', name: str = '', sort: str = 'Name', reverse: bool = False, limit: int = 0):
        """Iterate through list of nodes and print details"""

        if self.fetchData():
            # if JSON was requested and no filters, then just print it without iterating through
            if (self.format == 'json' and not (id or name or limit > 0)):
                print(json.dumps(self.nodes, indent=4))
                return

            for node in self.nodes:
                if (id or name):
                    if (id and 'id' in node and node['id'] == id) \
                        or (name and 'pretty_name' in node and name in node['pretty_name']):
                        self.print(node)
                else:
                    self.print(node)

            self.printFooter(sort=sort, reverse=reverse, limit=limit)

    def getNodeId(self, name: str):
        """Return Node Id for the location with the specified name. Only the first matching entry (exact match) is returned or empty string if not found"""

        if name and self.fetchData():
            # Iterate through list of nodes and find the specified one
            for node in self.nodes:
                if name in node['pretty_name']:
                    return node['id']

        return ''

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

    def print(self, node):
        """Print the data of the specified node"""

        if (self.format == 'json'):
            print(json.dumps(node, indent=4))
            return

        id = node['id']
        name = node['pretty_name']

        '''
        {
            "pretty_name": "Nuremberg, DE",
            "ip": "116.203.118.7",
            "ipv6": "2a01:4f8:c0c:c52d::1",
            "lastactive": 1682624703,
            "password": "***********",
            "username": "***********",
            "geodata": {
                "latitude": 49.460983,
                "longitude": 11.061859
            },
            "id": "60e81944f401963e610a0623"
        }
        '''
        self.table.add_row([id, name])
