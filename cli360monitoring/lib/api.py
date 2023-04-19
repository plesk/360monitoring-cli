#!/usr/bin/env python3

import requests
import json

from .config import Config
from .functions import printError

def toParamString(params):
    s = '?'
    for k, v in params.items():
        s += k + '=' + str(v) + '&'

    return s.rstrip('&')

def apiGet(path: str, expectedStatusCode: int, config: Config, params: dict = None):
    """Do a GET request and return JSON from response if expected status code was returned"""
    # check if headers are correctly set for authorization
    if not config.headers():
        return None

    if not params:
        params = config.params()

    if config.debug:
        print('GET', config.endpoint + path + toParamString(params))

    # Make request to API endpoint
    response = requests.get(config.endpoint + path, params=params, headers=config.headers())

    # Check status code of response
    if response.status_code == expectedStatusCode:
        # Return json from response
        return response.json()
    else:
        printError('An error occurred:', response.status_code)
        return None

def apiPost(path: str, config: Config, params: dict = None, data: dict = None, expectedStatusCode: int = 200, successMessage: str = '', errorMessage: str = ''):
    """Do a POST request"""
    # check if headers are correctly set for authorization
    if not config.headers():
        return False

    if not params:
        params = config.params()

    dataStr = json.dumps(data) if data else ''

    if config.debug:
        print('POST', config.endpoint + path + toParamString(params), dataStr)

    if config.readonly:
        return False

    # Make request to API endpoint
    response = requests.post(config.endpoint + path, data=dataStr, headers=config.headers())

    # Check status code of response
    if response.status_code == expectedStatusCode:
        if successMessage:
            print(successMessage)
        return True
    else:
        if errorMessage:
            print(errorMessage, '(status ' + str(response.status_code) + ')')
        return False

def apiPostJSON(path: str, config: Config, params: dict = None, data: dict = None):
    """Do a POST request"""
    # check if headers are correctly set for authorization
    if not config.headers():
        return None

    if not params:
        params = config.params()

    dataStr = json.dumps(data) if data else ''

    if config.debug:
        print('POST', config.endpoint + path + toParamString(params), dataStr)

    if config.readonly:
        return None

    # Make request to API endpoint
    response = requests.post(config.endpoint + path, data=dataStr, headers=config.headers())
    return response.json()

def apiPut(path: str, config: Config, params: dict = None, data: dict = None, expectedStatusCode: int = 200, successMessage: str = '', errorMessage: str = ''):
    """Do a PUT request"""
    # check if headers are correctly set for authorization
    if not config.headers():
        return False

    if not params:
        params = config.params()

    dataStr = json.dumps(data) if data else ''

    if config.debug:
        print('PUT', config.endpoint + path + toParamString(params), dataStr)

    if config.readonly:
        return False

    # Make request to API endpoint
    response = requests.put(config.endpoint + path, data=dataStr, headers=config.headers())

    # Check status code of response
    if response.status_code == expectedStatusCode:
        if successMessage:
            print(successMessage)
        return True
    else:
        if errorMessage:
            print(errorMessage, '(status ' + str(response.status_code) + ')')
        return False

def apiDelete(path: str, config: Config, params: dict = None, expectedStatusCode: int = 204, successMessage: str = '', errorMessage: str = ''):
    """Do a DELETE request"""
    # check if headers are correctly set for authorization
    if not config.headers():
        return False

    if not params:
        params = config.params()

    if config.debug:
        print('DELETE', config.endpoint + path + toParamString(params))

    if config.readonly:
        return False

    # Make request to API endpoint
    response = requests.delete(config.endpoint + path, headers=config.headers())

    # Check status code of response
    if response.status_code == expectedStatusCode:
        if successMessage:
            print(successMessage)
        return True
    else:
        if errorMessage:
            print(errorMessage, '(status ' + str(response.status_code) + ')')
        return False
