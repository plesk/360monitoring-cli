#!/usr/bin/env python3

import json
from prettytable import PrettyTable
from datetime import datetime

from .api import apiGet
from .config import Config
from .functions import printError, printWarn

class ServerNotifications(object):

    def __init__(self, config: Config, format: str = 'table'):
        self.config = config
        self.format = format
        self.notifications = None

        self.table = PrettyTable(field_names=['Start', 'End', 'Status', 'Summary'])
        self.table.align['Start'] = 'c'
        self.table.align['End'] = 'c'
        self.table.align['Status'] = 'c'
        self.table.align['Summary'] = 'l'

    def fetchData(self, serverId: str, startTimestamp: float, endTimestamp: float):
        """Retrieve a list of all alerts of a specified server in the specified time period"""

        # if data is already downloaded, use cached data
        if self.notifications != None:
            return True

        params = self.config.params()
        params['start'] = int(startTimestamp)
        params['end'] = int(endTimestamp)

        response_json = apiGet('server/' + serverId + '/notifications', 200, self.config, params)
        if response_json:
            if 'data' in response_json:
                self.notifications = response_json['data']
                return True
            else:
                printWarn('No notifications found for server', serverId)
                self.notifications = None
                return False
        else:
            self.notifications = None
            return False

    def list(self, serverId: str, startTimestamp: float, endTimestamp: float, sort: str = '', reverse: bool = False, limit: int = 0):
        """Iterate through list of server notifications and print details"""

        if self.fetchData(serverId, startTimestamp, endTimestamp):

            # if JSON was requested and no filters, then just print it without iterating through
            if self.format == 'json':
                print(json.dumps(self.notifications, indent=4))
                return

            # Iterate through list of servers and print data, etc.
            for notification in self.notifications:
                self.print(notification)

            self.printFooter(sort=sort, reverse=reverse, limit=limit)

    def printFooter(self, sort: str = '', reverse: bool = False, limit: int = 0):
        """Print table if table format requested"""

        if (self.format == 'table'):

            # if self.config.hide_ids:
            #     self.table.del_column('ID')

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

    def print(self, notification):
        """Print the data of the specified contact"""

        if (self.format == 'json'):
            print(json.dumps(notification, indent=4))
            return

        startTimestamp = datetime.fromtimestamp(float(notification['start']))
        endTimestamp = datetime.fromtimestamp(float(notification['end']))
        status = notification['status']
        summary = notification['summary']

        self.table.add_row([startTimestamp.strftime('%Y-%m-%d %H:%M:%S'), endTimestamp.strftime('%Y-%m-%d %H:%M:%S'), status, summary])
