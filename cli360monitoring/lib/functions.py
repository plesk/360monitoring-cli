#!/usr/bin/env python3

from datetime import datetime, timedelta
from .bcolors import bcolors

def printError(*args):
    print(f"{bcolors.FAIL}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")

def printWarn(*args):
    print(f"{bcolors.WARNING}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")

def formatDowntime(seconds):
    if seconds == 0:
        return 'none'
    elif seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes} minutes, {seconds} seconds"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 3600) % 60
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = ((seconds % 86400) % 3600) // 60
        seconds = ((seconds % 86400) % 3600) % 60
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def formatTimespan(startTimestamp, endTimestamp, dateTimeFormat: str = '%Y-%m-%d'):
    # if end date is today
    if datetime.today().strftime('%Y-%m-%d') == endTimestamp.strftime('%Y-%m-%d'):
        delta = endTimestamp - startTimestamp
        if delta.days == 365:
            return 'last 365 days'
        elif delta.days == 90:
            return 'last 90 days'
        elif delta.days == 30:
            return 'last 30 days'
        elif delta.days == 7:
            return 'last 7 days'
        elif delta.days == 1:
            return 'last 24 hours'

    startDateText = startTimestamp.strftime(dateTimeFormat)
    endDateText = endTimestamp.strftime(dateTimeFormat)
    if startDateText == endDateText:
        return startDateText
    else:
        return startDateText + ' - ' + endDateText
