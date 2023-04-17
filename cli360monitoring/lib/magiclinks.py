#!/usr/bin/env python3

import requests
import json
from datetime import datetime

from .config import Config
from .functions import printError, printWarn

class MagicLinks(object):

    def __init__(self, config):
        self.config = config

    def create(self, usertoken: str, serverId: str, magicLinkName: str):
        """Create a magic link for the specified server id"""

        if not usertoken:
            printError('No usertoken specified')
            return ''

        if not serverId:
            printError('No server id specified')
            return ''

        if not magicLinkName:
            printError('No name for the magic link specified')
            return ''

        # We can use the server id from the servers list to start creating an API Key for a specified server.
        # curl -XPOST --data "permission=read&name=cpanel&serverid={server_id}" "https://api.monitoring360.io/v1/user/{user_id}/keys?token={api_key}"

        data = {
            'permission': 'read',
            'name': magicLinkName,
            'serverid': serverId,
        }

        if self.config.debug:
            print('POST', self.config.endpoint + 'user/' + usertoken + '/keys?token=' + self.config.api_key, data)

        if self.config.readonly:
            return ''

        # Make request to API endpoint
        response = requests.post(self.config.endpoint + 'user/' + usertoken + '/keys?token=' + self.config.api_key, data=json.dumps(data), headers=self.config.headers())

        server_api_key = ''

        # Get api-key for this server from response
        response_json = response.json()
        if 'api_key' in response_json:
            server_api_key = response_json['api_key']
        else:
            printError('Failed to authenticate for server', serverId, 'with response code:', response.status_code)
            return ''

        # Make sure you set the right serverid in the data! Also replace the {user_id} in the URL. You can find your user_id once you click “add server”.
        # This API request return a new API_KEY which is specifically for this server only!

        # {"id":"********************","api_key":"********************"}

        # Now we can create the one-time-url:
        # curl -XPOST  "https://api.monitoring360.io/v1/auth?token={api_key}"
        # This should return the one-time-url:
        # {
        #     "token": "********************",
        #     "time": 1675709076,
        #     "serverid": {
        #         "$oid": "********************","
        #     },
        #     "url": "https://monitoring.platform360.io/auth/{server_id}/{}",
        #     "id": "********************","
        # }


        if self.config.debug:
            print('POST', self.config.endpoint + 'auth?token=' + server_api_key)

        if self.config.readonly:
            return False

        # Make request to API endpoint
        response = requests.post(self.config.endpoint + 'auth?token=' + server_api_key, headers=self.config.headers())

        # Get api-key for this server from response
        response_json = response.json()
        if 'url' in response_json:
            magiclink = response_json['url']
            print('Created one-time-url for server', serverId, magiclink)
            return magiclink
        else:
            printError('Failed to create one-time-url for server', serverId, 'with response code:', response.status_code)
            return ''
