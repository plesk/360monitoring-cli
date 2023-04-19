#!/usr/bin/env python3

import os
import argparse
import json
import subprocess
import sys
import webbrowser

from datetime import datetime, timedelta

# suprisingly this works in PyPi, but not locally. For local usage replace ".lib." with "lib."
# use "pip install -e ." to use "360monitoring" command with latest dev build locally based on local code.
from .lib.config import Config
from .lib.contacts import Contacts
from .lib.incidents import Incidents
from .lib.magiclinks import MagicLinks
from .lib.recommendations import Recommendations
from .lib.servers import Servers
from .lib.servernotifications import ServerNotifications
from .lib.sites import Sites
from .lib.sitenotifications import SiteNotifications
from .lib.statistics import Statistics
from .lib.usertokens import UserTokens
from .lib.wptoolkit import WPToolkit

__version__ = '1.0.17'

# only runs on Python 3.x; throw exception on 2.x
if sys.version_info[0] < 3:
    raise Exception("360 Monitoring CLI requires Python 3.x")

cfg = Config(__version__)
cli = argparse.ArgumentParser(prog='360monitoring', description='CLI for 360 Monitoring')
cli_subcommands = dict()

def check_version():
    """Check PyPi if there is a newer version of the application, but only once every 24 hours"""

    # some code parts have been introduced in Python 3.7 and are not supported on older versions
    if sys.version_info >= (3, 7):

        # skip version check if the last one was within 24 hours already
        if cfg.last_version_check and datetime.fromisoformat(cfg.last_version_check) > (datetime.now() - timedelta(hours=24)):
            return

        latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '360monitoringcli==random'], capture_output=True, text=True))
        latest_version = latest_version[latest_version.find('(from versions:')+15:]
        latest_version = latest_version[:latest_version.find(')')]
        latest_version = latest_version.replace(' ','').split(',')[-1]
        cfg.last_version_check = datetime.now().isoformat()
        cfg.saveToFile(False)

        if latest_version > __version__:
            print('Update available: Please upgrade from', __version__, 'to', latest_version, 'with: pip install 360monitoringcli --upgrade')

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

    if args.usertoken:
        cfg.usertoken = args.usertoken

    if args.debug:
        cfg.debug = args.debug == 'on'

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

# --- incidents functions ---

def incidents_add(args):
    """Sub command for incidents add"""
    incidents = Incidents(cfg)
    incidents.add(page_id=args.page_id, name=args.name, body=args.body)

def incidents_list(args):
    """Sub command for incidents list"""
    incidents = Incidents(cfg)
    incidents.format = args.output
    incidents.list(page_id=args.page_id, name=args.name)

def incidents_remove(args):
    """Sub command for incidents remove"""
    incidents = Incidents(cfg)
    incidents.remove(page_id=args.page_id, id=args.id, name=args.name)

def incidents(args):
    """Sub command for incidents"""
    cli_subcommands[args.subparser].print_help()

# --- magiclink functions ---

def magiclinks_create(args):
    """Sub command for magiclink create"""
    serverId = ''
    usertoken = args.usertoken if args.usertoken else cfg.usertoken

    if args.id:
        serverId = args.id
    elif args.name:
        # find correct server id for the server with the specified name
        servers = Servers(cfg)
        serverId = servers.getServerId(args.name)

    if usertoken and serverId:
        magiclinks = MagicLinks(cfg)
        magiclink = magiclinks.create(usertoken, serverId, 'Dashboard')

        if magiclink and args.open:
            webbrowser.open(magiclink)

        # if usertoken is not yet stored in config, do it now
        if not cfg.usertoken:
            cfg.usertoken = usertoken
            cfg.saveToFile(False)
    else:
        print('Please specify an existing server either by "--id id" or "--name hostname" and specifiy your user token "--usertoken token"')

def magiclinks(args):
    """Sub command for magiclink"""
    cli_subcommands[args.subparser].print_help()

# --- recommendations functions ---

def recommendations(args):
    """Sub command for recommendations"""
    recommendations = Recommendations(cfg)
    recommendations.print(format=args.output)

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

def servers_events(args):
    """Sub command for servers events"""
    serverId = ''
    startDate = datetime.strptime(args.start, '%Y-%m-%d') if args.start else (datetime.today() - timedelta(days=365))
    endDate = datetime.strptime(args.end, '%Y-%m-%d') if args.end else datetime.now()

    if args.id:
        serverId = args.id
    elif args.name:
        servers = Servers(cfg)
        serverId = servers.getServerId(args.name)

    if serverId:
        notifications = ServerNotifications(cfg)
        notifications.format = args.output
        notifications.list(serverId, startDate.timestamp(), endDate.timestamp(), args.sort, args.reverse, args.limit)

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

def sites_events(args):
    """Sub command for sites events"""
    siteId = ''
    startDate = datetime.strptime(args.start, '%Y-%m-%d') if args.start else (datetime.today() - timedelta(days=365))
    endDate = datetime.strptime(args.end, '%Y-%m-%d') if args.end else datetime.now()

    if args.id:
        siteId = args.id
    elif args.url:
        sites = Sites(cfg)
        siteId = sites.getSiteId(args.url)

    if siteId:
        notifications = SiteNotifications(cfg)
        notifications.format = args.output
        notifications.list(siteId, startDate.timestamp(), endDate.timestamp(), args.sort, args.reverse, args.limit)

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

def sites_uptime(args):
    """Sub command for sites uptime"""
    siteId = ''
    startDate = datetime.strptime(args.start, '%Y-%m-%d') if args.start else (datetime.today() - timedelta(days=365))
    endDate = datetime.strptime(args.end, '%Y-%m-%d') if args.end else datetime.now()
    sites = Sites(cfg)

    if args.id:
        siteId = args.id
    elif args.url:
        siteId = sites.getSiteId(args.url)
    elif args.name:
        siteId = sites.getSiteId(args.name)

    if siteId:
        if args.daily:
            periods = []
            firstDate = startDate
            while endDate > firstDate:
                startDate = datetime(endDate.year, endDate.month, endDate.day, 0, 0, 0)
                endDate = datetime(endDate.year, endDate.month, endDate.day, 23, 59, 59)
                periods.append([startDate.timestamp(), endDate.timestamp()])
                endDate = startDate - timedelta(days=1)
            sites.listUptimes(siteId, periods)
        elif args.monthly:
            periods = []
            firstDate = startDate
            while endDate > firstDate:
                startDate = datetime(endDate.year, endDate.month, 1, 0, 0, 0)
                endDate = datetime(endDate.year, endDate.month, endDate.day, 23, 59, 59)
                periods.append([startDate.timestamp(), endDate.timestamp()])
                endDate = startDate - timedelta(days=1)
            sites.listUptimes(siteId, periods, '%Y-%m')
        elif args.start or args.end:
            sites.listUptimes(siteId, [[startDate.timestamp(), endDate.timestamp()]])
        else:
            periods = []
            periods.append([(datetime.now() - timedelta(days=1)).timestamp(), datetime.now().timestamp()])
            periods.append([(datetime.now() - timedelta(days=7)).timestamp(), datetime.now().timestamp()])
            periods.append([(datetime.now() - timedelta(days=30)).timestamp(), datetime.now().timestamp()])
            periods.append([(datetime.now() - timedelta(days=90)).timestamp(), datetime.now().timestamp()])
            periods.append([(datetime.now() - timedelta(days=365)).timestamp(), datetime.now().timestamp()])
            sites.listUptimes(siteId, periods)

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
    usertokens.create(name=args.name, tags=args.tag)

def usertokens_list(args):
    """Sub command for usertokens list"""
    usertokens = UserTokens(cfg)
    usertokens.list(format=args.output)

def usertokens(args):
    """Sub command for usertokens"""
    cli_subcommands[args.subparser].print_help()

# --- wptoolkit functions ---

def wptoolkit(args):
    """Sub command for wptoolkit"""
    check_columns(args.columns)
    wptoolkit = WPToolkit(cfg)
    wptoolkit.print(format=args.output, issuesOnly=args.issues, sort=args.sort, reverse=args.reverse, limit=args.limit)

# --- configure & parse CLI ---

def performCLI():
    """Parse the command line parameters and call the related functions"""

    subparsers = cli.add_subparsers(title='commands', dest='subparser')
    cli.add_argument('-v', '--version', action='store_true', help='print CLI version')

    # config

    cli_config = subparsers.add_parser('config', help='configure connection to 360 Monitoring account')
    cli_config.set_defaults(func=config)
    cli_config_subparsers = cli_config.add_subparsers(title='commands', dest='subparser')

    cli_config_print = cli_config_subparsers.add_parser('print', help='print current settings for 360 Monitoring')
    cli_config_print.set_defaults(func=config_print)

    cli_config_save = cli_config_subparsers.add_parser('save', help='save current settings for 360 Monitoring to ' + cfg.filename)
    cli_config_save.set_defaults(func=config_save)
    cli_config_save.add_argument('--api-key', metavar='key', help='specify your API KEY for 360 Monitoring')
    cli_config_save.add_argument('--usertoken', metavar='token', help='specify your USERTOKEN for 360 Monitoring')
    cli_config_save.add_argument('--debug', choices=['on', 'off'], type=str, help='switch debug mode to print all API calls on or off')

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

    # incidents

    cli_incidents = subparsers.add_parser('incidents', help='list and manage incidents')
    cli_incidents.set_defaults(func=incidents)
    cli_incidents_subparsers = cli_incidents.add_subparsers(title='commands', dest='subparser')

    cli_incidents_add = cli_incidents_subparsers.add_parser('add', help='add a new incident')
    cli_incidents_add.set_defaults(func=incidents_add)
    cli_incidents_add.add_argument('--page-id', required=True, metavar='id', help='list incidents from status page with given ID')
    cli_incidents_add.add_argument('--name', required=True, metavar='name', help='name of the new incident')
    cli_incidents_add.add_argument('--body', metavar='body', help='text of the new incident')

    cli_incidents_list = cli_incidents_subparsers.add_parser('list', help='list incidents')
    cli_incidents_list.set_defaults(func=incidents_list)
    cli_incidents_list.add_argument('--page-id', required=True, metavar='id', help='list incidents from status page with given ID')
    cli_incidents_list.add_argument('--name', nargs='?', default='', metavar='name', help='list incidents with given name')

    cli_incidents_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_incidents_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_incidents_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_incidents_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    cli_incidents_remove = cli_incidents_subparsers.add_parser('remove', help='remove an incident')
    cli_incidents_remove.set_defaults(func=incidents_remove)
    cli_incidents_remove.add_argument('--page-id', required=True, metavar='id', help='remove incidents from status page with given ID')
    cli_incidents_remove.add_argument('--id', nargs='?', default='', metavar='id', help='remove incident with given ID')
    cli_incidents_remove.add_argument('--name', nargs='?', default='', metavar='name', help='remove incident with given name')

    # magiclinks

    cli_magiclinks = subparsers.add_parser('magiclinks', help='create a magic link for the dasboard of a specific server')
    cli_magiclinks.set_defaults(func=magiclinks)
    cli_magiclinks_subparsers = cli_magiclinks.add_subparsers(title='commands', dest='subparser')

    cli_magiclinks_create = cli_magiclinks_subparsers.add_parser('create', help='create new magic link to access the (readonly) dashboard for a specific server only')
    cli_magiclinks_create.set_defaults(func=magiclinks_create)
    cli_magiclinks_create.add_argument('--id', nargs='?', default='', metavar='id', help='create magic link for server with given ID')
    cli_magiclinks_create.add_argument('--name', nargs='?', default='', metavar='name', help='create magic link for server with given name')
    cli_magiclinks_create.add_argument('--usertoken', nargs='?', default='', metavar='token', help='use this usertoken for authentication')
    cli_magiclinks_create.add_argument('--open', action='store_true', help='open the server dashboard directly in the default web browser (optional)')

    # recommendations

    cli_recommendations = subparsers.add_parser('recommendations', help='show upgrade recommendations for servers that exceed their limits')
    cli_recommendations.set_defaults(func=recommendations)
    cli_recommendations.add_argument('--output', choices=['csv', 'table'], default='table', help='output format for the data')
    cli_recommendations.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_recommendations.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    # servers

    cli_servers = subparsers.add_parser('servers', help='list and manage monitored servers')
    cli_servers.set_defaults(func=servers)
    cli_servers_subparsers = cli_servers.add_subparsers(title='commands', dest='subparser')

    cli_servers_add = cli_servers_subparsers.add_parser('add', help='activate monitoring for a server')
    cli_servers_add.set_defaults(func=servers_add)

    cli_servers_events = cli_servers_subparsers.add_parser('events', help='list event notifications of a specified server')
    cli_servers_events.set_defaults(func=servers_events)
    cli_servers_events.add_argument('--id', nargs='?', default='', metavar='id', help='show event notifications for server with given ID')
    cli_servers_events.add_argument('--name', nargs='?', default='', metavar='name', help='show event notifications for server with given name')
    cli_servers_events.add_argument('--start', nargs='?', default='', metavar='start', help='select start date of notification period in form of yyyy-mm-dd')
    cli_servers_events.add_argument('--end', nargs='?', default='', metavar='end', help='select end date of notification period in form of yyyy-mm-dd')

    cli_servers_events.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_servers_events.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_servers_events.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_servers_events.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_servers_events.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_servers_events.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_servers_events.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_servers_events.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

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

    cli_sites_events = cli_sites_subparsers.add_parser('events', help='list event notifications of a specified site')
    cli_sites_events.set_defaults(func=sites_events)
    cli_sites_events.add_argument('--id', nargs='?', default='', metavar='id', help='show event notifications for site with given ID')
    cli_sites_events.add_argument('--url', nargs='?', default='', metavar='url', help='show event notifications for site with given url')
    cli_sites_events.add_argument('--start', nargs='?', default='', metavar='start', help='select start date of notification period in form of yyyy-mm-dd')
    cli_sites_events.add_argument('--end', nargs='?', default='', metavar='end', help='select end date of notification period in form of yyyy-mm-dd')

    cli_sites_events.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_sites_events.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_sites_events.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_sites_events.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_sites_events.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_sites_events.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_sites_events.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_sites_events.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

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

    cli_sites_uptime = cli_sites_subparsers.add_parser('uptime', help='show uptime')
    cli_sites_uptime.set_defaults(func=sites_uptime)
    cli_sites_uptime.add_argument('--id', nargs='?', default='', metavar='id', help='show uptime for site with given ID')
    cli_sites_uptime.add_argument('--url', nargs='?', default='', metavar='url', help='show uptime for site with given url')
    cli_sites_uptime.add_argument('--name', nargs='?', default='', metavar='name', help='show uptime for site with given name')
    cli_sites_uptime.add_argument('--start', nargs='?', default='', metavar='start', help='select start date of uptime period in form of yyyy-mm-dd')
    cli_sites_uptime.add_argument('--end', nargs='?', default='', metavar='end', help='select end date of uptime period in form of yyyy-mm-dd')
    cli_sites_uptime.add_argument('--daily', action='store_true', help='show uptime per day')
    cli_sites_uptime.add_argument('--monthly', action='store_true', help='show uptime per month')

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
    cli_usertokens_create.add_argument('--name', nargs='?', default='', metavar='name', help='name of the new token (optional)')
    cli_usertokens_create.add_argument('--tag', nargs='?', default='', metavar='tag', help='set a tag for the new token (optional)')

    cli_usertokens_list = cli_usertokens_subparsers.add_parser('list', help='list usertokens')
    cli_usertokens_list.set_defaults(func=usertokens_list)
    cli_usertokens_list.add_argument('--output', choices=['json', 'csv', 'table'], default='table', help='output format for the data')
    cli_usertokens_list.add_argument('--json', action='store_const', const='json', dest='output', help='print data in JSON format')
    cli_usertokens_list.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_usertokens_list.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    # wptoolkit

    cli_wptoolkit = subparsers.add_parser('wptoolkit', help='list statistics of WP Toolkit if installed')
    cli_wptoolkit.set_defaults(func=wptoolkit)

    cli_wptoolkit.add_argument('--issues', action='store_true', help='show only servers with WordPress issues')
    cli_wptoolkit.add_argument('--columns', nargs='*', default='', metavar='col', help='specify columns to print in table view or remove columns with 0 as prefix e.g. "0id"')
    cli_wptoolkit.add_argument('--sort', nargs='?', default='', metavar='col', help='sort by specified column. Reverse sort by adding --reverse')
    cli_wptoolkit.add_argument('--reverse', action='store_true', help='show in descending order. Works only together with --sort')
    cli_wptoolkit.add_argument('--limit', nargs='?', default=0, type=int, metavar='n', help='limit the number of printed items')

    cli_wptoolkit.add_argument('--output', choices=['csv', 'table'], default='table', help='output format for the data')
    cli_wptoolkit.add_argument('--csv', action='store_const', const='csv', dest='output', help='print data in CSV format')
    cli_wptoolkit.add_argument('--table', action='store_const', const='table', dest='output', help='print data as ASCII table')

    # Parse

    cli_subcommands['config'] = cli_config
    cli_subcommands['contacts'] = cli_contacts
    cli_subcommands['dashboard'] = cli_dashboard
    cli_subcommands['incidents'] = cli_incidents
    cli_subcommands['magiclinks'] = cli_magiclinks
    cli_subcommands['recommendations'] = cli_recommendations
    cli_subcommands['servers'] = cli_servers
    cli_subcommands['signup'] = cli_signup
    cli_subcommands['sites'] = cli_sites
    cli_subcommands['statistics'] = cli_statistics
    cli_subcommands['usertokens'] = cli_usertokens
    cli_subcommands['wptoolkit'] = cli_wptoolkit

    args = cli.parse_args()
    if args.subparser == None:
        if args.version:
            print('360 Monitoring CLI Version:', __version__)
        elif 'func' in args:
            # recommendations, statistics, signup, wptoolkit and dashboard is shown directly without subparser
            if args.func == config:
                cli_config.print_help()
            elif args.func == contacts:
                cli_contacts.print_help()
            elif args.func == incidents:
                cli_incidents.print_help()
            elif args.func == magiclinks:
                cli_magiclinks.print_help()
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
    check_version()
    performCLI()

if __name__ == '__main__':
    main()
