#!/usr/bin/env python3

import os
import argparse
import json

# suprisingly this works in PyPi, but not locally. For local usage replace ".lib." with "lib."
from .lib.monitoringconfig import MonitoringConfig
from .lib.contacts import Contacts
from .lib.servers import Servers
from .lib.sites import Sites
from .lib.usertokens import UserTokens
from .lib.statistics import Statistics

__version__ = '1.0.6'

monitoringconfig = MonitoringConfig()
cli = argparse.ArgumentParser(description='CLI for 360 Monitoring')
cli_subcommands = dict()

def config(args):
    """Sub command for config"""
    if args.api_key:
        monitoringconfig.api_key = args.api_key
        monitoringconfig.saveToFile()

    elif args.save:
        monitoringconfig.saveToFile()

    else:
        monitoringconfig.print()

def statistics(args):
    """Sub command for statistics"""
    statistics = Statistics(monitoringconfig)
    statistics.format = args.format
    statistics.print()

def servers(args):
    """Sub command for servers"""
    servers = Servers(monitoringconfig)
    servers.format = args.format

    if args.list:
        servers.list()

    elif args.get:
        servers.printHeader()

        for server in args.get:
            servers.get(server)

        servers.printFooter()

    elif args.add:
        usertokens = UserTokens(monitoringconfig)
        token = usertokens.token()
        if not token:
            print("First create a user token by executing:")
            print()
            print("360monitoring usertokens --create")
            print("360monitoring usertokens --list")
            print()
            token = "[YOUR_USER_TOKEN]"

        print("Please login via SSH to each of the servers you would like to add and execute the following command:")
        print()
        print("wget -q -N monitoring.platform360.io/agent360.sh && bash agent360.sh", token)

    elif args.remove:
        print("Please login via SSH to each of the servers you would like to remove.")
        print("First stop the monitoring agent by running \"service agent360 stop\" then run \"pip3 uninstall agent360\". After 15 minutes you are able to remove the server.")

    else:
        cli_subcommands[args.subparser].print_help()

def sites(args):
    """Sub command for sites"""
    sites = Sites(monitoringconfig)
    sites.format = args.format

    if args.list:
        sites.list()

    elif args.get:
        sites.printHeader()

        for monitor in args.get:
            sites.get(monitor)

        sites.printFooter()

    elif args.add:
        for url in args.add:
            sites.add(url, protocol=args.protocol, name=args.name, force=args.force)

    elif args.remove:
        for monitor in args.remove:
            sites.remove(monitor)

    elif args.add_from_file:
        if os.path.isfile(args.add_from_file):
            with open(args.add_from_file) as file:
                lines = file.readlines()
                for line in lines:
                    sites.add(line.strip())
        else:
            print("ERROR: File to import ", args.add_from_file, "not found")

    else:
        cli_subcommands[args.subparser].print_help()

def contacts(args):
    """Sub command for contacts"""
    contacts = Contacts(monitoringconfig)
    contacts.format = args.format

    if args.list:
        contacts.list()

    elif args.get:
        contacts.printHeader()

        for contact in args.get:
            contacts.get(contact)

        contacts.printFooter()

    elif args.add:
        for contact in args.add:
            contacts.add(contact, email=args.email, sms=args.sms)

    elif args.remove:
        for contact in args.remove:
            contacts.remove(contact)

    elif args.add_from_file:
        if os.path.isfile(args.add_from_file):
            with open(args.add_from_file) as file:
                lines = file.readlines()
                for line in lines:
                    contacts.add(line.strip(), "")
        else:
            print("ERROR: File to import ", args.add_from_file, "not found")

    else:
        cli_subcommands[args.subparser].print_help()

def usertokens(args):
    """Sub command for usertokens"""
    usertokens = UserTokens(monitoringconfig)
    usertokens.format = args.format

    if args.list:
        usertokens.list()

    elif args.get:
        usertokens.printHeader()

        for usertoken in args.get:
            usertokens.get(usertoken)

        usertokens.printFooter()

    elif args.create:
        usertokens.create()

    else:
        cli_subcommands[args.subparser].print_help()

def performCLI():
    """Parse the command line parameters and call the related functions"""

    subparsers = cli.add_subparsers(title='commands', dest='subparser')
    cli.add_argument('-v', '--version', action='store_true', help='print CLI version')

    cli_config = subparsers.add_parser('config', help='configure connection to 360 Monitoring account')
    cli_config.set_defaults(func=config)
    cli_config.add_argument('-a', '--api-key', metavar='key', help='specify your API KEY for 360 Monitoring')
    cli_config.add_argument('-p', '--print', action='store_true', help='print your current settings for 360 Monitoring')
    cli_config.add_argument('-s', '--save', action='store_true', help='save your current settings for 360 Monitoring to the default ini file')

    cli_servers = subparsers.add_parser('servers', help='list and manage all monitored servers')
    cli_servers.set_defaults(func=servers)
    group_servers = cli_servers.add_mutually_exclusive_group()
    group_servers.add_argument('-a', '--add', action='store_true', help='explain how to add a server monitor')
    group_servers.add_argument('-g', '--get', nargs='+', metavar='name', help='servers to print')
    group_servers.add_argument('-l', '--list', action='store_true', help='list all monitored servers')
    group_servers.add_argument('-r', '--remove', action='store_true', help='explain how to add a server monitor')

    cli_servers.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_servers.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_servers.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_servers.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_sites = subparsers.add_parser('sites', help='list and manage all monitored websites')
    cli_sites.set_defaults(func=sites)
    group_sites = cli_sites.add_mutually_exclusive_group()
    group_sites.add_argument('-a', '--add', nargs='+', metavar='url', help='URL(s) to add')
    group_sites.add_argument('-g', '--get', nargs='+', metavar='url', help='URL(s) to print')
    group_sites.add_argument('-l', '--list', action='store_true', help='list all monitored urls')
    group_sites.add_argument('-r', '--remove', nargs='+', metavar='url', help='URL(s) to remove')
    group_sites.add_argument('-f', '--add-from-file', metavar='filepath', help='file containing one URL per line to add')

    cli_sites.add_argument('--name', nargs='?', default='', metavar='name', help='give the new monitor a specific name. Otherwise the url is used as name.')
    cli_sites.add_argument('--protocol', nargs='?', default='https', metavar='protocol', help='specify a different protocol than https')
#    cli_sites.add_argument('--port', nargs='?', default=443, type=int, metavar='port', help='specify a different port than 443')
    cli_sites.add_argument('--force', action='store_true', help='add new monitor even if already exists')

    cli_sites.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_sites.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_sites.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_sites.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_contacts = subparsers.add_parser('contacts', help='list and manage all contacts')
    cli_contacts.set_defaults(func=contacts)
    group_contacts = cli_contacts.add_mutually_exclusive_group()
    group_contacts.add_argument('-a', '--add', nargs='+', metavar='name', help='contact to add')
    group_contacts.add_argument('-g', '--get', nargs='+', metavar='name', help='contact to print')
    group_contacts.add_argument('-l', '--list', action='store_true', help='list all contacts')
    group_contacts.add_argument('-r', '--remove', nargs='+', metavar='name', help='contact to remove')
    group_contacts.add_argument('-f', '--add-from-file', metavar='filepath', help='file containing one contact per line to add')

    cli_contacts.add_argument('--email', nargs='?', default='', metavar='email', help='email address for the new contact.')
    cli_contacts.add_argument('--sms', nargs='?', default='', metavar='phone_number', help='mobile phone number for the new contact.')

    cli_contacts.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_contacts.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_contacts.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_contacts.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_usertokens = subparsers.add_parser('usertokens', help='list or create usertokens')
    cli_usertokens.set_defaults(func=usertokens)
    group_contacts = cli_usertokens.add_mutually_exclusive_group()
    group_contacts.add_argument('-c', '--create', action='store_true', help='create new user token')
    group_contacts.add_argument('-g', '--get', nargs='+', help='usertoken to print')
    group_contacts.add_argument('-l', '--list', action='store_true', help='list all usertokens')

    cli_usertokens.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_usertokens.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_usertokens.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_usertokens.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_statistics = subparsers.add_parser('statistics', help='print statistics')
    cli_statistics.set_defaults(func=statistics)
    cli_statistics.add_argument('-p', '--print', action='store_true', help='print statistics for 360 Monitoring')
    cli_statistics.add_argument('--format', choices=['csv', 'table'], default='table', help='output format for the data')
    cli_statistics.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_statistics.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_subcommands['config'] = cli_config
    cli_subcommands['contacts'] = cli_contacts
    cli_subcommands['servers'] = cli_servers
    cli_subcommands['sites'] = cli_sites
    cli_subcommands['usertokens'] = cli_usertokens
    cli_subcommands['statistics'] = cli_statistics

    args = cli.parse_args()
    if args.subparser == None:
        if args.version:
            print('360 Monitoring CLI Version:', __version__)
        else:
            cli.print_help()
    else:
        args.func(args)

def main():
    performCLI()

if __name__ == '__main__':
    main()
