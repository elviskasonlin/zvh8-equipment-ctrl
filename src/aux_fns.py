#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 2023

@author: elviskasonlin
"""

import json
import pathlib

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

def load_configuration(fileName: str):
    """
    Returns the default variables in the specified json file in the config folder as a dictionary
    Args:
        * fileName (`str`): The name of the configuraiton file without the file type suffix
    Returns:
        * (`dict`): Configuration data as a dictionary
    """
    # Specifying the location of the save file (default to be in the parent folder)
    file_loc = pathlib.Path("." + "/config/" + fileName + ".json")
    data_as_dict = None

    try:
        f = open(file_loc, "r")
        data_as_dict = json.load(f)
        f.close()
    except Exception as err:
        print("ERROR:O In load_configuration with msg ", err)

    return data_as_dict

def save_configuration(fileName: str, configData: dict):
    """
    Saves user settings as a json file in the config folder from a dictionary
    Args:
        * fileName (`str`): The name of the configuraiton file without the file type suffix
        * configData (`dict`): The configuration data
    Returns:
        * None
    """

    # Setting up a default file location
    # Creates the "config" directory if it doesn't exist
    dir_loc = pathlib.Path("." + "/config/")
    dir_loc.mkdir(parents=True, exist_ok=True)

    # Specifying the location of the save file (default to be in the parent folder)
    file_loc = pathlib.Path("." + "/config/" + fileName + ".json")

    # Write the data
    f = open(file_loc, "w")
    json.dump(configData, f)
    f.close()

    return