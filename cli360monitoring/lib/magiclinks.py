#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from prettytable import PrettyTable

from .config import Config
from .functions import printError, printWarn

class MagicLinks(object):

    def __init__(self, config):
        self.config = config

    def create(self, server_id: str):
        """Create a magic link for the specified server id"""

        # We can use the server id from the servers list to start creating an API Key for a specified server.

        # curl -XPOST --data "permission=read&name=cpanel&serverid={server_id}" "https://api.monitoring360.io/v1/user/USER_ID/keys?token={api_key}"

        # Make sure you set the right serverid in the data! Also replace the USER_ID in the URL. You can find your user_id once you click “add server”.
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

        print('Not implemented yet')
