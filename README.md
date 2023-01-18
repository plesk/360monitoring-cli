# 360 Monitoring CLI

This repository contains a CLI script for 360 Monitoring that allows you to connect to your 360 Monitoring (https://360monitoring.com) account and list monitoring data, add, update or remove server or website monitors.

## Documentation

You can find the full documentation including the feature complete REST API at [docs.360monitoring.com](https://docs.360monitoring.com/docs) and [docs.360monitoring.com/docs/api](https://docs.360monitoring.com/docs/api).

## Preconditions

 * Make sure to have an account at https://360monitoring.com or https://platform360.io
 * Make sure to install Python 3.0 and pip3
 * Install the Python modules "requests", "json", "argparse" and "prettytable"
 * Please configure your 360 Monitoring API Key by running ./360monitoring config --api-key YOUR_API_KEY

## Install required Python modules

    $ pip3 install requests
    $ pip3 install prettytable

## Usage

    $ ./360monitoring.py config --api-key KEY   configure API KEY to connect to 360 Monitoring account
    $ ./360monitoring.py servers --list         display all monitored servers
    $ ./360monitoring.py sites --list           display all monitored sites
    $ ./360monitoring.py --help                 display general help
    $ ./360monitoring.py contacts --help        display specific help for a sub command

