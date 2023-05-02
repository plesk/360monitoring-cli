#!/usr/bin/env python3

import json
from datetime import datetime

from .api import apiGet
from .config import Config
from .functions import printError, printWarn

class ServerCharts(object):

    def __init__(self, config: Config):
        self.config = config

    def create(self, serverId: str, metric: str = 'cpu', startTimestamp: float = 0, endTimestamp: float = 0, dataAsJSON: bool = False):
        """Create a server metrics chart for the specified server id"""

        if not serverId:
            printError('No server id specified')
            return ''

        if not metric:
            printError('No metric specified: e.g. use \"cpu\"')
            return ''

        params = self.config.params()

        if not dataAsJSON:
            params['output'] = 'png'
        # metrics can be one of [bitninja, cpu, httpd, mem, network, nginx, ping, process, swap, uptime, wp-toolkit]
        params['metric'] = metric
        if startTimestamp > 0:
            params['start'] = int(startTimestamp)
        if endTimestamp > 0:
            params['end'] = int(endTimestamp)

        response_json = apiGet('server/' + serverId + '/metrics', 200, self.config, params)
        if response_json:
            if dataAsJSON:
                print(json.dumps(response_json, indent=4))
                return ''
            elif 'uri' in response_json:
                uri = response_json['uri']
                print(uri)
                return uri
            else:
                printWarn('Server with id', serverId, 'not found')
                return ''
        else:
            return ''
