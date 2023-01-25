#!/usr/bin/env python3

import os
import argparse
from lib.monitoringconfig import MonitoringConfig
from lib.contacts import Contacts
from lib.servers import Servers
from lib.sites import Sites
from lib.usertokens import UserTokens
import json

__version__ = '1.0.2'

monitoringconfig = MonitoringConfig()
cli = argparse.ArgumentParser(description='CLI for 360 Monitoring')
cli_subcommands = dict()

def config(args):
    """Sub command for config"""
    if args.api_key:
        monitoringconfig.api_key = args.api_key
        monitoringconfig.save_to_file()

    elif args.save:
        monitoringconfig.save_to_file()

    else:
        monitoringconfig.print()

def servers(args):
    """Sub command for servers"""
    servers = Servers(monitoringconfig)
    servers.format = args.format

    if args.list:
        servers.list()

    elif args.get:
        servers.print_header()

        for server in args.get:
            servers.get(server)

        servers.print_footer()

    elif args.add:
        usertokens = UserTokens(monitoringconfig)
        token = usertokens.token()
        if not token:
            print("First create a user token by executing:")
            print()
            print("./360monitoring.py usertokens --create")
            print("./360monitoring.py usertokens --list")
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
        sites.print_header()

        for monitor in args.get:
            sites.get(monitor)

        sites.print_footer()

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
        contacts.print_header()

        for contact in args.get:
            contacts.get(contact)

        contacts.print_footer()

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
        usertokens.print_header()

        for usertoken in args.get:
            usertokens.get(usertoken)

        usertokens.print_footer()

    elif args.create:
        usertokens.create()

    else:
        cli_subcommands[args.subparser].print_help()

def perform_cli():
    """Parse the command line parameters and call the related functions"""

    subparsers = cli.add_subparsers(title='commands', dest='subparser')
    cli.add_argument('-v', '--version', action='store_true', help='print CLI version')

    cli_config = subparsers.add_parser('config', help='configure connection to 360 Monitoring account')
    cli_config.set_defaults(func=config)
    cli_config.add_argument('-a', '--api-key', help='specify your API KEY for 360 Monitoring')
    cli_config.add_argument('-p', '--print', action='store_true', help='print your current settings for 360 Monitoring')
    cli_config.add_argument('-s', '--save', action='store_true', help='save your current settings for 360 Monitoring to the default ini file')

    cli_servers = subparsers.add_parser('servers', help='list and manage all monitored servers')
    cli_servers.set_defaults(func=servers)
    cli_servers.add_argument('-a', '--add', action='store_true', help='explain how to add a server monitor')
    cli_servers.add_argument('-g', '--get', nargs='+', help='servers to print')
    cli_servers.add_argument('-l', '--list', action='store_true', help='list all monitored servers')
    cli_servers.add_argument('-r', '--remove', action='store_true', help='explain how to add a server monitor')

    cli_servers.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_servers.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_servers.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_servers.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_sites = subparsers.add_parser('sites', help='list and manage all monitored websites')
    cli_sites.set_defaults(func=sites)
    cli_sites.add_argument('-a', '--add', nargs='+', help='URL(s) to add')
    cli_sites.add_argument('-g', '--get', nargs='+', help='URL(s) to print')
    cli_sites.add_argument('-l', '--list', action='store_true', help='list all monitored urls')
    cli_sites.add_argument('-r', '--remove', nargs='+', help='URL(s) to remove')
    cli_sites.add_argument('-f', '--add-from-file', help='file containing one URL per line to add')

    cli_sites.add_argument('--name', nargs='?', default='', help='give the new monitor a specific name. Otherwise the url is used as name.')
    cli_sites.add_argument('--protocol', nargs='?', default='https', help='specify a different protocol than https')
    cli_sites.add_argument('--force', action='store_true', help='add new monitor even if already exists')

    cli_sites.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_sites.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_sites.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_sites.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_contacts = subparsers.add_parser('contacts', help='list and manage all contacts')
    cli_contacts.set_defaults(func=contacts)
    cli_contacts.add_argument('-a', '--add', nargs='+', help='contact to add')
    cli_contacts.add_argument('-g', '--get', nargs='+', help='contact to print')
    cli_contacts.add_argument('-l', '--list', action='store_true', help='list all contacts')
    cli_contacts.add_argument('-r', '--remove', nargs='+', help='contact to remove')
    cli_contacts.add_argument('-f', '--add-from-file', help='file containing one contact per line to add')

    cli_contacts.add_argument('--email', nargs='?', default='', help='email address for the new contact.')
    cli_contacts.add_argument('--sms', nargs='?', default='', help='mobile phone number for the new contact.')

    cli_contacts.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_contacts.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_contacts.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_contacts.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_usertokens = subparsers.add_parser('usertokens', help='list or create usertokens')
    cli_usertokens.set_defaults(func=usertokens)
    cli_usertokens.add_argument('-c', '--create', action='store_true', help='create new user token')
    cli_usertokens.add_argument('-g', '--get', nargs='+', help='usertoken to print')
    cli_usertokens.add_argument('-l', '--list', action='store_true', help='list all usertokens')

    cli_usertokens.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_usertokens.add_argument('--json', action='store_const', const='json', dest='format', help='print data in JSON format')
    cli_usertokens.add_argument('--csv', action='store_const', const='csv', dest='format', help='print data in CSV format')
    cli_usertokens.add_argument('--table', action='store_const', const='table', dest='format', help='print data as ASCII table')

    cli_subcommands['config'] = cli_config
    cli_subcommands['contacts'] = cli_contacts
    cli_subcommands['servers'] = cli_servers
    cli_subcommands['sites'] = cli_sites
    cli_subcommands['usertokens'] = cli_usertokens

    args = cli.parse_args()
    if args.subparser == None:
        if args.version:
            print('360 Monitoring CLI Version:', __version__)
        else:
            cli.print_help()
    else:
        args.func(args)

def main():
    perform_cli()

if __name__ == '__main__':
    main()
