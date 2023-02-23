#!/usr/bin/env python3

import os
import argparse
import json
import webbrowser

# suprisingly this works in PyPi, but not locally. For local usage replace ".lib." with "lib."
from .lib.config import Config
from .lib.contacts import Contacts
from .lib.servers import Servers
from .lib.sites import Sites
from .lib.usertokens import UserTokens
from .lib.statistics import Statistics

__version__ = '1.0.12'

cfg = Config(__version__)
cli = argparse.ArgumentParser(prog='360monitoring', description='CLI for 360 Monitoring')
cli_subcommands = dict()

def check_columns(columns):
    """Show or hide columns in ASCII table view"""
    for column in columns:
        if '0id' == column.lower():
            cfg.hide_ids = True
        elif 'id' == column.lower():
            cfg.hide_ids = False

# --- config functions ---

def config_print(args):
    """Sub command for config print"""
    cfg.print()

def config_save(args):
    """Sub command for config save"""
    if args.api_key:
        cfg.api_key = args.api_key

    cfg.saveToFile()

def config(args):
    """Sub command for config"""
    config_print(args)

# --- contacts functions ---

def contacts_add(args):
    """Sub command for contacts add"""
    contacts = Contacts(cfg)

    if args.file:
        if os.path.isfile(args.file):
            with open(args.file) as file:
                lines = file.readlines()
                for line in lines:
                    contacts.add(line.strip())
        else:
            print('ERROR: File', args.file, 'to import not found')
    elif args.name:
        contacts.add(name=args.name, email=args.email, sms=args.sms)
    else:
        print('You need to specify at least a name with --name [name]')

def contacts_list(args):
    """Sub command for contacts list"""
    check_columns(args.columns)
    contacts = Contacts(cfg)
    contacts.format = args.output
    contacts.list(id=args.id, name=args.name, email=args.email, phone=args.phone, sort=args.sort, reverse=args.reverse, limit=args.limit)

def contacts_remove(args):
    """Sub command for contacts remove"""
    contacts = Contacts(cfg)
    contacts.remove(id=args.id, name=args.name, email=args.email, phone=args.phone)

def contacts(args):
    """Sub command for contacts"""
    cli_subcommands[args.subparser].print_help()

# --- dashboard functions ---

def dashboard(args):
    """Sub command for dashboard"""
    webbrowser.open('https://monitoring.platform360.io/')

# --- servers functions ---

def servers_add(args):
    """Sub command for servers add"""
    usertokens = UserTokens(cfg)
    token = usertokens.token()
    if not token:
        print('First create a user token by executing:')
        print()
        print('360monitoring usertokens create')
        print('360monitoring usertokens list')
        print()
        token = '[YOUR_USER_TOKEN]'

    print('Please login via SSH to each of the servers you would like to add and execute the following command:')
    print()
    print('wget -q -N monitoring.platform360.io/agent360.sh && bash agent360.sh', token)

def servers_list(args):
    """Sub command for servers list"""
    check_columns(args.columns)
    servers = Servers(cfg)
    servers.format = args.output
    servers.list(args.issues, args.sort, args.reverse, args.limit, args.tag)

def servers_remove(args):
    """Sub command for servers remove"""
    print("Please login via SSH to each of the servers you would like to remove.")
    print("First stop the monitoring agent by running \"service agent360 stop\" then run \"pip3 uninstall agent360\". After 15 minutes you are able to remove the server.")

def servers_update(args):
    """Sub command for servers update"""
    servers = Servers(cfg)
    pattern = ''
    if args.id:
        pattern = args.id
    elif args.name:
        pattern = args.name
    servers.setTags(pattern, args.tag)

def servers(args):
    """Sub command for servers"""
    cli_subcommands[args.subparser].print_help()

# --- signup functions ---

def signup(args):
    """Sub command for signup"""
    webbrowser.open('https://360monitoring.com/monitoring-trial/')

# --- sites functions ---

def sites_add(args):
    """Sub command for sites add"""
    sites = Sites(cfg)

    if args.file:
        if os.path.isfile(args.file):
            with open(args.file) as file:
                lines = file.readlines()
                for line in lines:
                    sites.add(line.strip())
        else:
            print('ERROR: File', args.file, 'to import not found')
    elif args.url:
        sites.add(args.url, protocol=args.protocol, name=args.name, force=args.force)
    else:
        print('You need to specify at least a name with --name [name]')

def sites_list(args):
    """Sub command for sites list"""
    check_columns(args.columns)
    sites = Sites(cfg)
    sites.format = args.output
    sites.list(id=args.id, url=args.url, name=args.name, location=args.location, pattern=args.pattern, issuesOnly=args.issues, sort=args.sort, reverse=args.reverse, limit=args.limit)

def sites_remove(args):
    """Sub command for sites remove"""
    sites = Sites(cfg)
    sites.remove(id=args.id, url=args.url, name=args.name, location=args.location, pattern=args.pattern)

def sites(args):
    """Sub command for sites"""
    cli_subcommands[args.subparser].print_help()

# --- statistics functions ---

def statistics(args):
    """Sub command for statistics"""
    statistics = Statistics(cfg)
    statistics.print(format=args.output)

# --- usertokens functions ---

def usertokens_create(args):
    """Sub command for usertokens create"""
    usertokens = UserTokens(cfg)
    usertokens.create()

def usertokens_list(args):
    """Sub command for usertokens list"""
    usertokens = UserTokens(cfg)
    usertokens.list(format=args.output)

def usertokens(args):
    """Sub command for usertokens"""
    cli_subcommands[args.subparser].print_help()

def performCLI():
    """Parse the command line parameters and call the related functions"""

    subparsers = cli.add_subparsers(title='commands', dest='subparser')
    cli.add_argument('-v', '--version', action='store_true', help='print CLI version')

    # config

    cli_config = subparsers.add_parser('config', help='configure connection to 360 Monitoring account')
    cli_config.set_defaults(func=config)

    config_subparsers = cli_config.add_subparsers(title='commands', dest='subparser')

    cli_config_print = config_subparsers.add_parser('print', help='print current settings for 360 Monitoring')
    cli_config_print.set_defaults(func=config_print)

    cli_config_save = config_subparsers.add_parser('save', help='save current settings for 360 Monitoring to ' + cfg.filename)
    cli_config_save.set_defaults(func=config_save)
    cli_config_save.add_argument('-a', '--api-key', metavar='key', help='specify your API KEY for 360 Monitoring')

    # contacts

    cli_contacts = subparsers.add_parser('contacts', help='list and manage contacts')
    cli_contacts.set_defaults(func=contacts)
    cli_contacts_subparsers = cli_contacts.add_subparsers(title='commands', dest='subparser')

    cli_contacts_add = cli_contacts_subparsers.add_parser('add', help='add a new contact')
    cli_contacts_add.set_defaults(func=contacts_add)
    cli_contacts_add.add_argument('--name', nargs='?', metavar='name', help='name of the new contact')
    cli_contacts_add.add_argument('--email', nargs='?', default='', metavar='email', help='email address of the new contact')
    cli_contacts_add.add_argument('--sms', nargs='?', default='', metavar='phone', help='mobile phone number of the new contact (optional)')
    cli_contacts_add.add_argument('--file', nargs='?', default='', metavar='file', help='file containing one contact per line to add')

    cli_contacts_list = cli_contacts_subparsers.add_parser('list', help='list contacts')
    cli_contacts_list.set_defaults(func=contacts_list)
    cli_contacts_list.add_argument('--id', nargs='?', default='', metavar='id', help='list contact with given ID')
    cli_contacts_list.add_argument('--name', nargs='?', default='', metavar='name', help='list contact with given name')
    cli_contacts_list.add_argument('--email', nargs='?', default='', metavar='email', help='list contact with given email address')
    cli_contacts_list.add_argument('--phone', nargs='?', default='', metavar='phone', help='list contact with given phone number')

    cli_contacts_list.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_contacts_list.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_contacts_list.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_contacts_list.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_contacts_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_contacts_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_contacts_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_contacts_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    cli_contacts_remove = cli_contacts_subparsers.add_parser('remove', help='remove a contact')
    cli_contacts_remove.set_defaults(func=contacts_remove)
    cli_contacts_remove.add_argument('--id', nargs='?', default='', metavar='id', help='remove contact with given ID')
    cli_contacts_remove.add_argument('--name', nargs='?', default='', metavar='name', help='remove contact with given name')
    cli_contacts_remove.add_argument('--email', nargs='?', default='', metavar='email', help='remove contact with given email address')
    cli_contacts_remove.add_argument('--phone', nargs='?', default='', metavar='phone', help='remove contact with given phone number')

    # dashboard

    cli_dashboard = subparsers.add_parser('dashboard', help='open 360 Monitoring Dashboard in your Web Browser')
    cli_dashboard.set_defaults(func=dashboard)

    # servers

    cli_servers = subparsers.add_parser('servers', help='list and manage monitored servers')
    cli_servers.set_defaults(func=servers)
    cli_servers_subparsers = cli_servers.add_subparsers(title='commands', dest='subparser')

    cli_servers_add = cli_servers_subparsers.add_parser('add', help='activate monitoring for a server')
    cli_servers_add.set_defaults(func=servers_add)

    cli_servers_list = cli_servers_subparsers.add_parser('list', help='list monitored servers')
    cli_servers_list.set_defaults(func=servers_list)
    cli_servers_list.add_argument('--id', nargs='?', default='', metavar='id', help='update server with given ID')
    cli_servers_list.add_argument('--name', nargs='?', default='', metavar='name', help='update server with given name')
    cli_servers_list.add_argument('--tag', nargs='*', default='', metavar='tag', help='only list servers matching these tags')
    cli_servers_list.add_argument('--issues', action='store_true', help='show only servers with issues')

    cli_servers_list.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_servers_list.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_servers_list.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_servers_list.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_servers_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_servers_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_servers_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_servers_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    cli_servers_remove = cli_servers_subparsers.add_parser('remove', help='remove monitoring for a server')
    cli_servers_remove.set_defaults(func=servers_remove)

    cli_servers_update = cli_servers_subparsers.add_parser('update', help='set tags for a server')
    cli_servers_update.set_defaults(func=servers_update)
    cli_servers_update.add_argument('--id', nargs='?', default='', metavar='id', help='update server with given ID')
    cli_servers_update.add_argument('--name', nargs='?', default='', metavar='name', help='update server with given name')
    cli_servers_update.add_argument('--tag', nargs='*', default='', metavar='tag', help='set these tags for one or more servers specified')

    # signup

    cli_signup = subparsers.add_parser('signup', help='sign up for 360 Monitoring')
    cli_signup.set_defaults(func=signup)

    # sites

    cli_sites = subparsers.add_parser('sites', help='list and manage monitored websites')
    cli_sites.set_defaults(func=sites)
    cli_sites_subparsers = cli_sites.add_subparsers(title='commands', dest='subparser')

    cli_sites_add = cli_sites_subparsers.add_parser('add', help='activate monitoring for a site')
    cli_sites_add.set_defaults(func=sites_add)
    cli_sites_add.add_argument('--url', nargs='?', metavar='url', help='url of site that should be monitored')
    cli_sites_add.add_argument('--name', nargs='?', metavar='name', help='name of site that should be monitored (optional)')
    cli_sites_add.add_argument('--protocol', nargs='?', default='https', metavar='protocol', help='specify a different protocol than https')
#    cli_sites_add.add_argument('--port', nargs='?', default=443, type=int, metavar='port', help='specify a different port than 443')
    cli_sites_add.add_argument('--force', action='store_true', help='add new monitor even if already exists')
    cli_sites_add.add_argument('--file', nargs='?', default='', metavar='file', help='file containing one URL per line to monitor')

    cli_sites_list = cli_sites_subparsers.add_parser('list', help='list sites')
    cli_sites_list.set_defaults(func=sites_list)
    cli_sites_list.add_argument('--id', nargs='?', default='', metavar='id', help='list site with given ID')
    cli_sites_list.add_argument('--url', nargs='?', default='', metavar='url', help='list site with given url')
    cli_sites_list.add_argument('--name', nargs='?', default='', metavar='name', help='list site with given name')
    cli_sites_list.add_argument('--location', nargs='?', default='', metavar='location', help='list sites monitored from given location')
    cli_sites_list.add_argument('--pattern', nargs='?', default='', metavar='pattern', help='list sites with pattern included in URL')
    cli_sites_list.add_argument('--issues', action='store_true', help='show only sites with issues')

    cli_sites_list.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_sites_list.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_sites_list.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_sites_list.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_sites_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_sites_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_sites_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_sites_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    cli_sites_remove = cli_sites_subparsers.add_parser('remove', help='remove a contact')
    cli_sites_remove.set_defaults(func=sites_remove)
    cli_sites_remove.add_argument('--id', nargs='?', default='', metavar='id', help='remove site with given ID')
    cli_sites_remove.add_argument('--url', nargs='?', default='', metavar='url', help='remove site with given url')
    cli_sites_remove.add_argument('--name', nargs='?', default='', metavar='name', help='remove site with given name')
    cli_sites_remove.add_argument('--location', nargs='?', default='', metavar='location', help='remove sites monitored from given location')
    cli_sites_remove.add_argument('--pattern', nargs='?', default='', metavar='pattern', help='remove sites with pattern included in URL')

    # statistics

    cli_statistics = subparsers.add_parser('statistics', help='print statistics')
    cli_statistics.set_defaults(func=statistics)
    cli_statistics.add_argument('--output', choices=['csv', 'table'], default='table', help='output format for the data')
    cli_statistics.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_statistics.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    # user tokens

    cli_usertokens = subparsers.add_parser('usertokens', help='list or create usertokens')
    cli_usertokens.set_defaults(func=usertokens)
    cli_usertokens_subparsers = cli_usertokens.add_subparsers(title='commands', dest='subparser')

    cli_usertokens_create = cli_usertokens_subparsers.add_parser('create', help='create new user token')
    cli_usertokens_create.set_defaults(func=usertokens_create)

    cli_usertokens_list = cli_usertokens_subparsers.add_parser('list', help='list usertokens')
    cli_usertokens_list.set_defaults(func=usertokens_list)
    cli_usertokens_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_usertokens_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_usertokens_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_usertokens_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    # Parse

    cli_subcommands['config'] = cli_config
    cli_subcommands['contacts'] = cli_contacts
    cli_subcommands['dashboard'] = cli_dashboard
    cli_subcommands['servers'] = cli_servers
    cli_subcommands['signup'] = cli_signup
    cli_subcommands['sites'] = cli_sites
    cli_subcommands['statistics'] = cli_statistics
    cli_subcommands['usertokens'] = cli_usertokens

    args = cli.parse_args()
    if args.subparser == None:
        if args.version:
            print('360 Monitoring CLI Version:', __version__)
        elif 'func' in args:
            # statistics, signup and dashboard is shown directly without subparser
            if args.func == config:
                cli_config.print_help()
            elif args.func == contacts:
                cli_contacts.print_help()
            elif args.func == servers:
                cli_servers.print_help()
            elif args.func == sites:
                cli_sites.print_help()
            elif args.func == usertokens:
                cli_usertokens.print_help()
            else:
                cli.print_help()
        else:
            cli.print_help()
    else:
        args.func(args)

def main():
    performCLI()

if __name__ == '__main__':
    main()
