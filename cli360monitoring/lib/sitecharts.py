#!/usr/bin/env python3

import json
from datetime import datetime

from .api import apiGet
from .config import Config
from .functions import printError, printWarn

class SiteCharts(object):

    def __init__(self, config: Config):
        self.config = config

    def create(self, siteId: str, startTimestamp: float = 0, endTimestamp: float = 0):
        """Create a site metrics chart for the specified site id"""

        if not siteId:
            printError('No site id specified')
            return ''

        params = self.config.params()
        params['output'] = 'png'
        if startTimestamp > 0:
            params['start'] = int(startTimestamp)
        if endTimestamp > 0:
            params['end'] = int(endTimestamp)

        response_json = apiGet('monitor/' + siteId + '/metrics', 200, self.config, params)
        if response_json:
            print(json.dumps(response_json, indent=4))
            print()
            print('Only JSON output supported currently. PNG export not yet implemented.')
            '''
            if 'uri' in response_json:
                uri = response_json['uri']
                print(uri)
                return uri
            else:
                printWarn('Site with id', siteId, 'not found')
                return ''
            '''
        else:
            return ''
