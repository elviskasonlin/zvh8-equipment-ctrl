#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 2023

@author: elviskasonlin
"""

import json
import pathlib
import os
from typing import Callable

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
        "VNA_START_FREQ": 450,
        "VNA_STOP_FREQ": 1250,
        "VNA_CAL_KIT_ID": "FSH-Z28",
        "VNA_STATE_FILE": "CTRL_CAL_STATE.SET",
        "FIELD_NAMES": ["Timestamp / HH:MM:SS.SS", "Sweep points / #", "Freq / Hz", "Mag. / dB", "Impedence / Ohm", "Trace Data", "FSR Resistance / Ohm", "FSR Voltage / V", "Cutoff Mag / dB", "Bandwidth / MHz", "Q Factor at Cutoff Mag", "Start freq / MHz", "Stop freq / MHz"]
    }
    return CONFIGURATION_VARS

def get_user_input(display_text: str, return_type: str):
    """
    Gets the user's choice using input()
    Args:
        * display_text (`str`): The text to be displayed in `input()`
        * return_type (`str`): The target conversion. Available types are `float`, `int`, and `bool`. Default is string.
    Returns:
        * (`str`, `bool`, `int`, `float`) The user's input converted to the target type as specified in `return_type`
    """

    buffer = None
    output = None

    while True:
        buffer = input(display_text)
        try:
            if (return_type == "float"):
                output = float(buffer)
                break
            elif (return_type == "int"):
                output = int(buffer)
                break
            elif (return_type == "bool"):
                output = buffer
                match output:
                    case "Yes" | "yes" | "Y" | "y" | 1 | "T" | "t" | "True" | "true":
                        output = True
                    case "No" | "no" | "N" | "n" | 0 | "F" | "f" | "False" | "false":
                        output = False
                    case _:
                        raise ValueError
                break
            else:
                output = buffer
                break
        except ValueError:
            print("ERROR An invalid input was detected. Please enter again.")
            continue

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
    if not os.path.exists(dir_loc):
        os.makedirs(dir_loc, exist_ok=False)

    # Specifying the location of the save file (default to be in the parent folder)
    file_loc = dir_loc.joinpath(fileName + ".json")
    print(f"File saving at {file_loc}")
    # Write the data
    f = open(file_loc, "w") # 'w': For writing. File is created if it does not exist
    json.dump(configData, f)
    f.close()

    return


# def empty_dict_buffers(field_names: list, replace_with):
#     new_buffer = dict
#     for each in field_names:
#         print(each)
#         new_buffer.update(dict(each=replace_with))
#     return new_buffer