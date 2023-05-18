#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instrumentation control and data acquisition script
For use in collecting the data from both the Vector Network Analyser and the Arduino (that is connected to force-sensing resistors)
Currently implemented for Rohde and Schwarz ZVH8 Cable and Antenna Analyser and Arduino Uno (5V)

Version Alpha 1.0

Created on Tue May 16 17:32:29 2023
@author: elviskasonlin
"""

import src.aux_fns as AUXFN
import src.conn_arduino as ARDCONN
import src.conn_rsinstrument as INSTCONN
import src.gui as GUI

import copy
import pathlib

def main():

    # Set the configuration variables up
    CONFIG_VARS = dict()
    DEFAULT_CONFIG_VARS = AUXFN.get_default_configuration()
    CURRENT_WORKING_DIR = pathlib.Path.cwd()
    print(CURRENT_WORKING_DIR)

    try:
        CONFIG_VARS = AUXFN.load_configuration(currentWorkingDir=CURRENT_WORKING_DIR, fileName=DEFAULT_CONFIG_VARS["CONFIG_FILE_NAME"],directoryName=DEFAULT_CONFIG_VARS["CONFIG_FOLDER"]) # See if configuration variables json file already exists
    except FileNotFoundError: # If the configuration variables json file does not exist, create one from the default configuration
        CONFIG_VARS = copy.deepcopy(DEFAULT_CONFIG_VARS)
        AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,fileName=CONFIG_VARS["CONFIG_FILE_NAME"], directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
        print("WARNING Configuration file not found. Loaded default configuration! Saved a new configuration file with default settings.")

    # Initialise a variable for user input when user browses through the menus
    menu_choice = -1

    while (menu_choice != 0):
        print(GUI.get_menu_text(menuName="main_menu"))
        menu_choice = AUXFN.get_user_choice(displayText="Input: ", returnType="int")

        if (menu_choice == 1):
            # Device Initialisation

            # Initialise Devices
            CONFIG_VARS["ARDUINO_PORT"] = "COM3"
            serialObject, ARD_CONN_READY = ARDCONN.establish_connection(configVariables=CONFIG_VARS)
            print(ARD_CONN_READY)

            # Check whether both devices are initialised by checking the status flags
            # Implement status flags

            print("All devices initialised")
            menu_choice = -1
        elif (menu_choice == 2):
            # Settings
            # Set the settings required for initialisation
            # Set a default setting if no settings file is found

            print(GUI.get_menu_text(menuName="settings_menu"))
            menu_choice = AUXFN.get_user_choice(displayText="Input: ", returnType="int")
            match menu_choice:
                case 1:
                    print("Change save folder name to: ")
                case 2:
                    print("Change save file name to: ")
                case 3:
                    print("Change arduino port to: ")
                case 4:
                    print("Change R&S instrument port to: ")
                case 5:
                    AUXFN.save_configuration(CONFIGURATION_VARS["F"])
                case _:
                    pass

            menu_choice = -1
        elif (menu_choice == 2):
            # Data Acquisition

            # Check for the status flag
            # Start data acquisition process

            menu_choice = -1
        else:
            print("NOTICE: Exiting program...")

    return

if __name__ == '__main__':
    main()