#!/usr/bin/env python3

from .bcolors import bcolors

def printError(*args):
    print(f"{bcolors.FAIL}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")

def printWarn(*args):
    print(f"{bcolors.WARNING}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")
