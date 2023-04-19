#!/usr/bin/env python3

from prettytable import PrettyTable

from .config import Config
from .servers import Servers

class WPToolkit(object):

    def __init__(self, config: Config):
        self.config = config

        self.table = PrettyTable(field_names=['ID', 'Server name', 'WP sites', 'Alive', 'Outdated', 'Outdated PHP', 'Broken'])
        self.table.align['ID'] = 'l'
        self.table.align['Server name'] = 'l'
        self.table.min_width['Server name'] = 24
        self.table.align['WP sites'] = 'r'
        self.table.align['Alive'] = 'r'
        self.table.align['Outdated'] = 'r'
        self.table.align['Outdated PHP'] = 'r'
        self.table.align['Broken'] = 'r'

        self.num_servers_with_wpt = 0
        self.sum_wp_sites_total = 0
        self.sum_wp_sites_alive = 0
        self.sum_wp_sites_outdated = 0
        self.sum_wp_sites_outdated_php = 0
        self.sum_wp_sites_broken = 0

    def printFooter(self, sort: str = '', reverse: bool = False, limit: int = 0):
        """Print table if table format requested"""

        # add summary row as table footer
        self.table.add_row(['', 'Sum of ' + str(self.num_servers_with_wpt) + ' servers', self.sum_wp_sites_total, self.sum_wp_sites_alive, self.sum_wp_sites_outdated, self.sum_wp_sites_outdated_php, self.sum_wp_sites_broken])

        if self.config.hide_ids:
            self.table.del_column('ID')

        # Get string to be printed and create list of elements separated by \n
        list_of_table_lines = self.table.get_string().split('\n')

        # remember summary row
        summary_line = list_of_table_lines[-2]

        # remove summary row again to allow sorting and limiting
        self.table.del_row(len(self.table.rows)-1)

        if sort:
            # if sort contains the column index instead of the column name, get the column name instead
            if sort.isdecimal():
                sort = self.table.get_csv_string().split(',')[int(sort) - 1]
        else:
            sort = None

        if limit > 0:
            list_of_table_lines = self.table.get_string(sortby=sort, reversesort=reverse, start=0, end=limit).split('\n')
        else:
            list_of_table_lines = self.table.get_string(sortby=sort, reversesort=reverse).split('\n')

        # Sorting by multiple columns could be done like this
        # list_of_table_lines = self.table.get_string(sortby=("Col Name 1", "Col Name 2")), reversesort=reverse).split('\n')

        # Print the table
        print('\n'.join(list_of_table_lines))
        print(summary_line)
        print(list_of_table_lines[0])

    def print(self, format: str = 'table', issuesOnly: bool = False, sort: str = '', reverse: bool = False, limit: int = 0):
        """Iterate through all servers and aggregate metrics for those that have WP Toolkit installed"""

        servers = Servers(self.config)
        if servers.fetchData():
            for server in servers.servers:
                id = server['id']
                name = server['name']
                last_data = server['last_data']
                if last_data and 'wp-toolkit' in last_data:
                    wpt_data = last_data['wp-toolkit']
                    if wpt_data:
                        wp_sites_total = wpt_data['WordPress Websites']
                        wp_sites_alive = wpt_data['WordPress Websites - Alive']
                        wp_sites_outdated = wpt_data['WordPress Websites - Outdated']
                        wp_sites_outdated_php = wpt_data['WordPress Websites - Outdated PHP']
                        wp_sites_broken = wpt_data['WordPress Websites - Broken']

                        self.num_servers_with_wpt += 1
                        self.sum_wp_sites_total += wp_sites_total
                        self.sum_wp_sites_alive += wp_sites_alive
                        self.sum_wp_sites_outdated += wp_sites_outdated
                        self.sum_wp_sites_outdated_php += wp_sites_outdated_php
                        self.sum_wp_sites_broken += wp_sites_broken

                        if wp_sites_outdated > 0 or wp_sites_outdated_php > 0 or wp_sites_broken > 0 or not issuesOnly:
                            self.table.add_row([id, name, wp_sites_total, wp_sites_alive, wp_sites_outdated, wp_sites_outdated_php, wp_sites_broken])

        if (format == 'table'):
            self.printFooter(sort=sort, reverse=reverse, limit=limit)
        elif (format == 'csv'):
            print(self.table.get_csv_string(delimiter=self.config.delimiter))
