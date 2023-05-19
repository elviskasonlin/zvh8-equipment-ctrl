#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 2023

@author: elviskasonlin
"""

import json
import pathlib
import os

def get_default_configuration():
    CONFIGURATION_VARS = {
        "ARDUINO_PORT": "/dev/tty.usbmodem14101",
        "ARDUINO_BAUD": 9600,
        "ARDUINO_CONN_PARITY": "N",
        "ARDUINO_CONN_TIMEOUT": 0,
        "ARDUINO_HSHK_TIMEOUT": 6.0,
        "ARDUINO_HSHK_POLLRATE": 0.2,
        "VNA_RESOURCE": "TCPIP0::172.16.10.10::INSTR",
        "OUTPUT_FOLDER": r'results',
        "OUTPUT_FILE_NAME": r'logfile',
        "CONFIG_FOLDER": r'config',
        "CONFIG_FILE_NAME": r'config',
        "VNA_POINTS": 401,
        "VNA_START_FREQ": 750,
        "VNA_STOP_FREQ": 1150,
        "VNA_CAL_KIT_ID": "FSH-Z28"
    }
    return CONFIGURATION_VARS

def get_user_choice(displayText: str, returnType: str):
    """
    Gets the user's choice using input()
    Args:
        * display_text (`str`): The text to be displayed in `input()`
        * return_type (`str`): The target conversion.
    Returns:
        * (`str`, `bool`, `int`, `float`): The user's input converted to the target type as specified in `return_type`
    """

    buffer = input(displayText)
    output = None

    try:
        if (returnType == "float"):
            output = float(buffer)
        elif (returnType == "int"):
            output = int(buffer)
        elif (returnType == "bool"):
            output = bool(int(buffer))
        else:
            output = buffer
    except Exception as err:
        print("ERROR: In get_user_choice with msg ", err)
        pass

    return output

def load_configuration(currentWorkingDir: pathlib.Path, fileName: str, directoryName: str):
    """
    Returns the default variables in the specified json file in the config folder as a dictionary
    Args:
        * fileName (`str`): The name of the configuration file without the file type suffix
        * directoryName (`str`): The name of the directory the configuration file will reside in
    Returns:
        * (`dict`): Configuration data as a dictionary
    """
    # Specifying the location of the save file (default to be in the parent folder)
    file_loc = currentWorkingDir.joinpath(f"{directoryName}/" + fileName + ".json")
    print(file_loc)
    data_as_dict = None

    # try:
    f = open(file_loc, "r")
    data_as_dict = json.load(f)
    f.close()
    # except Exception as err:
    # print("ERROR: Configuration load issue in load_configuration with msg ", err)
    # return Exception

    return data_as_dict

def save_configuration(currentWorkingDir: pathlib.Path, fileName: str, directoryName: str, configData: dict):
    """
    Saves user settings as a json file in the config folder from a dictionary
    Args:
        * fileName (`str`): The name of the configuration file without the file type suffix
        * directoryName (`str`): The name of the directory the configuration file will reside in
        * configData (`dict`): The configuration data
    Returns:
        * None
    """

    # Setting up a default file location
    # Creates the "config" directory if it doesn't exist
    dir_loc = currentWorkingDir.joinpath(f"{directoryName}/")
    os.mkdir(dir_loc)

    # Specifying the location of the save file (default to be in the parent folder)
    file_loc = dir_loc.joinpath(fileName + ".json")
    print(f"File saving at {file_loc}")
    # Write the data
    f = open(file_loc, "w")
    json.dump(configData, f)
    f.close()

    return