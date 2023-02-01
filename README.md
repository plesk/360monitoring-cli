# 360 Monitoring CLI

This repository contains a CLI script for 360 Monitoring that allows you to connect to your 360 Monitoring (https://360monitoring.com) account and list monitoring data, add, update or remove server or website monitors.

## Documentation

You can find the full documentation including the feature complete REST API at [docs.360monitoring.com](https://docs.360monitoring.com/docs) and [docs.360monitoring.com/docs/api](https://docs.360monitoring.com/docs/api).

## Preconditions

 * Make sure to have an account at https://360monitoring.com or https://platform360.io
 * Make sure to install Python 3.0 and pip3

 ## Preconditions for local testing

 * To test the code locally, install the Python modules "requests", "configparser", "argparse" and "prettytable"
 * Create an alias for "360monitoring=./cli360monitoring.py"
 * To test a package from staging you can simply deploy a docker container:

    $ docker run -it --rm pypy:3-7-slim-buster /bin/bash

 * ... and install the test package from https://test.pypi.org/

    $ pip install -i https://test.pypi.org/simple/ --force-reinstall -v "360monitoringcli==1.0.5"

## Install 360 Monitoring CLI as ready-to-use package

    $ pip3 install 360monitoring
## Local testing only: Install required Python modules

    $ pip3 install requests
    $ pip3 install configparser
    $ pip3 install argparse
    $ pip3 install prettytable

## Configure your account

First you need to connect your CLI to your existing 360 Monitoring account via your API KEY. If you don't have a 360 Monitoring account yet, please register for free at https://360monitoring.com. To create an API KEY you'll need to upgrade at least to a Pro plan to be able to create your API KEY.

    $ 360monitoring config --api-key KEY     configure API KEY to connect to 360 Monitoring account

## Usage

    $ 360monitoring --help                   display general help
    $ 360monitoring statistics               display all assets of your account
    $ 360monitoring servers --list           display all monitored servers
    $ 360monitoring sites --list             display all monitored sites
    $ 360monitoring contacts --list          display all contacts
    $ 360monitoring usertokens --list        display user tokens
    $ 360monitoring config --print           display your current settings and where those are stored

    $ 360monitoring sites --add domain.tld   start monitoring a new website

    $ 360monitoring contacts --help          display specific help for a sub command
