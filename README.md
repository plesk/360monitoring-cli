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
    $ pip3 install configparser
    $ pip3 install argparse
    $ pip3 install prettytable

## Configure your account

First you need to connect your CLI to your existing 360 Monitoring account via your API KEY. If you don't have a 360 Monitoring account yet, please register for free at https://360monitoring.com. To create an API KEY you'll need to upgrade at least to a Pro plan to be able to create your API KEY.

    $ ./360monitoring.py config --api-key KEY     configure API KEY to connect to 360 Monitoring account

## Usage

    $ ./360monitoring.py --help                   display general help
    $ ./360monitoring.py servers --list           display all monitored servers
    $ ./360monitoring.py sites --list             display all monitored sites
    $ ./360monitoring.py contacts --list          display all contacts
    $ ./360monitoring.py usertokens --list        display user tokens

    $ ./360monitoring.py sites --add domain.tld   start monitoring a new website

    $ ./360monitoring.py contacts --help          display specific help for a sub command
