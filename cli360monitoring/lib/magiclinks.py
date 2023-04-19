#!/usr/bin/env python3

from datetime import datetime

from .api import apiGet, apiPostJSON
from .config import Config
from .functions import printError, printWarn

class MagicLinks(object):

    def __init__(self, config: Config):
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

        data = {
            'permission': 'read',
            'name': magicLinkName,
            'serverid': serverId,
        }
        response_json = apiPostJSON('user/' + usertoken + '/keys?token=' + self.config.api_key, self.config, data=data)

        # Get api-key for this server from response
        server_api_key = ''
        if 'api_key' in response_json:
            server_api_key = response_json['api_key']
        else:
            printError('Failed to authenticate for server', serverId)
            return ''

        response_json = apiPostJSON('auth?token=' + server_api_key, self.config)

        # Get one-time-url for this server from response
        if 'url' in response_json:
            magiclink = response_json['url']
            print('Created one-time-url for server', serverId, magiclink)
            return magiclink
        else:
            printError('Failed to create one-time-url for server', serverId)
            return ''
