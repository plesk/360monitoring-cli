#!/usr/bin/env python3

from prettytable import PrettyTable

from .config import Config
from .servers import Servers

class Recommendations(object):

    def __init__(self, config: Config):
        self.config = config

        self.table = PrettyTable(field_names=['Asset', 'Recommendation'])
        self.table.align['Asset'] = 'l'
        self.table.align['Recommendation'] = 'l'

    def print(self, format: str = 'table'):
        """Iterate through all assets and check for which we have recommendations"""

        servers = Servers(self.config)
        if servers.fetchData():
            for server in servers.servers:
                if servers.hasIssue(server):
                    self.table.add_row([server['name'], servers.getRecommendation(server)])

        if (format == 'table'):
            print(self.table)
        elif (format == 'csv'):
            print(self.table.get_csv_string(delimiter=self.config.delimiter))
