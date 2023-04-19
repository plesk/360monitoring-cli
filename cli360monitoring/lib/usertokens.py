#!/usr/bin/env python3

import json
from prettytable import PrettyTable

from .api import apiGet, apiPost
from .config import Config
from .functions import printError, printWarn

class UserTokens(object):

    def __init__(self, config: Config):
        self.config = config
        self.usertokens = None

        self.table = PrettyTable(field_names=['Token', 'Name', 'Tags'])
        self.table.align['Token'] = 'l'
        self.table.align['Name'] = 'l'
        self.table.align['Tags'] = 'l'

    def fetchData(self):
        """Retrieve the list of all usertokens"""

        # if data is already downloaded, use cached data
        if self.usertokens != None:
            return True

        response_json = apiGet('usertoken', 200, self.config)
        if response_json:
            if 'tokens' in response_json:
                self.usertokens = response_json['tokens']
                return True
            else:
                printWarn('No usertokens found')
                self.usertokens = None
                return False
        else:
            self.usertokens = None
            return False

    def list(self, token: str = '', format: str = 'table'):
        """Iterate through list of usertokens and print details"""

        if self.fetchData():
            if self.usertokens != None:

                # if JSON was requested and no filters, then just print it without iterating through
                if (format == 'json' and not token):
                    print(json.dumps(self.usertokens, indent=4))
                    return

                for usertoken in self.usertokens:
                    if token:
                        if usertoken['token'] == token:
                            self.print(usertoken)
                            break
                    else:
                        self.print(usertoken)

            if (format == 'table'):
                print(self.table)
            elif (format == 'csv'):
                print(self.table.get_csv_string(delimiter=self.config.delimiter))

    def token(self):
        """Print the data of first usertoken"""

        if self.fetchData() and len(self.usertokens) > 0:
            return self.usertokens[0]['token']

    def create(self, name: str = '', tags: str = ''):
        """Create a new usertoken"""

        data = {
            'name': name,
            'tags': tags
        }

        return apiPost('usertoken', self.config, data=data, expectedStatusCode=200, successMessage='Created usertoken', errorMessage='Failed to create usertoken')

    def print(self, usertoken, format: str = 'table'):
        """Print the data of the specified usertoken"""

        if (format == 'json'):
            print(json.dumps(usertoken, indent=4))
            return

        token = usertoken['token']
        name = usertoken['name'] if 'name' in usertoken and usertoken['name'] else ''

        tags = ''
        if 'tags' in usertoken and usertoken['tags']:
            for tag in usertoken['tags']:
                tags += ', ' + tag

        self.table.add_row([token, name, tags.lstrip(', ')])
