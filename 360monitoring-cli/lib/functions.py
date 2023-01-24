#!/usr/bin/env python3
from lib.bcolors import bcolors

def print_error(*args):
    print(f"{bcolors.FAIL}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")

def print_warn(*args):
    print(f"{bcolors.WARNING}", sep='', end='')
    print(*args, f"{bcolors.ENDC}")
