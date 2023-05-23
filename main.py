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
import serial.tools.list_ports

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

    # See if configuration variables json file already exists
    try:
        CONFIG_VARS = AUXFN.load_configuration(currentWorkingDir=CURRENT_WORKING_DIR, fileName=DEFAULT_CONFIG_VARS["CONFIG_FILE_NAME"],directoryName=DEFAULT_CONFIG_VARS["CONFIG_FOLDER"])
    except FileNotFoundError:
        # If the configuration variables json file does not exist, create one from the default configuration
        CONFIG_VARS = copy.deepcopy(DEFAULT_CONFIG_VARS)
        AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,fileName=CONFIG_VARS["CONFIG_FILE_NAME"], directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
        print("WARNING Configuration file not found. Loaded default configuration! Saved a new configuration file with default settings.")

    # Initialise a variable for user input when user browses through the menus
    menu_choice = -1

    # Initialise objects and status flags
    serialObject, RSINST, ARD_CONN_IS_READY, RSINST_CONN_IS_READY = None, None, False, False

    while (menu_choice != 0):
        print(GUI.get_menu_text(menuName="main_menu"))
        menu_choice = AUXFN.get_user_choice(displayText="Input: ", returnType="int")

        if (menu_choice == 1):
            # Device Initialisation

            # Initialise Arduino Serial
            CONFIG_VARS["ARDUINO_PORT"] = "COM3"
            serialObject, ARD_CONN_IS_READY = ARDCONN.establish_connection(configVariables=CONFIG_VARS)
            print("DEBUG Arduino Connection Status:", ARD_CONN_IS_READY)

            # Initialise R&S VNA
            RSINST, RSINST_CONN_IS_READY = INSTCONN.establish_connection(configVars=CONFIG_VARS)
            print("DEBUG RS Inst. Connection Status:", RSINST_CONN_IS_READY)

            if (ARD_CONN_IS_READY == False) or (RSINST_CONN_IS_READY == False):
                print("Failed to initialise one or more devices. Please check your connections and try again")

            menu_choice = -1
        elif (menu_choice == 2):
            # Settings
            # Set the settings required for initialisation
            # Set a default setting if no settings file is found

            print(GUI.get_menu_text(menuName="settings_menu"))
            menu_choice = AUXFN.get_user_choice(displayText="Input: ", returnType="int")
            match menu_choice:
                case 1:
                    print("Change save folder name")
                    print(f"Current save folder name is: {CONFIG_VARS['OUTPUT_FOLDER']}")

                    choice, fname = str(), str()
                    while (fname != "0"):
                        fname = AUXFN.get_user_choice(displayText="Change folder name to ([0] to cancel): ", returnType="str")
                        if (fname == "0"):
                            print("Returning back to menu...")
                            break
                        choice = AUXFN.get_user_choice(displayText=f"You have entered `{fname}`, confirm? [Y]es [N]o: ", returnType="str")
                        match choice:
                            case "Y" | "y" | "Yes" | "yes":
                                print("Updating configuration file with new output folder name...")
                                CONFIG_VARS["OUTPUT_FOLDER"] = fname
                                AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,
                                                         fileName=CONFIG_VARS["CONFIG_FILE_NAME"],
                                                         directoryName=CONFIG_VARS["CONFIG_FOLDER"],
                                                         configData=CONFIG_VARS)
                                break
                            case "N" | "n" | "No" | "no":
                                continue
                            case _:
                                print("An invalid entry, please try again")
                                continue
                case 2:
                    print("Change save file name")
                    print(f"Current save file name is: {CONFIG_VARS['OUTPUT_FILE_NAME']}")

                    choice, fname = str(), str()
                    while (fname != "0"):
                        fname = AUXFN.get_user_choice(displayText="Change file name to ([0] to cancel): ", returnType="str")
                        if (fname == "0"):
                            print("Returning back to menu...")
                            break
                        choice = AUXFN.get_user_choice(displayText=f"You have entered `{fname}`, confirm? [Y]es [N]o: ", returnType="str")
                        match choice:
                            case "Y" | "y" | "Yes" | "yes":
                                print("Updating configuration file with new output file name...")
                                CONFIG_VARS["OUTPUT_FILE_NAME"] = fname
                                AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,
                                                         fileName=CONFIG_VARS["CONFIG_FILE_NAME"],
                                                         directoryName=CONFIG_VARS["CONFIG_FOLDER"],
                                                         configData=CONFIG_VARS)
                                break
                            case "N" | "n" | "No" | "no":
                                continue
                            case _:
                                print("An invalid entry, please try again")
                                continue
                case 3:
                    # Check for available serial ports and get the device paths as string list
                    available_serial_dvcs = serial.tools.list_ports.comports()
                    available_serial_dvcs_in_strlist = list()
                    for each in available_serial_dvcs:
                        available_serial_dvcs_in_strlist.append(each.device)
                    print(f"Current port is: {CONFIG_VARS['ARDUINO_PORT']}")
                    print(f"Here are the available ports: {available_serial_dvcs_in_strlist}")

                    # Get port choice
                    port_choice = str()
                    while (port_choice not in available_serial_dvcs_in_strlist and port_choice != "0"):
                        port_choice = AUXFN.get_user_choice(displayText="Enter a valid port path ([0] to cancel): ", returnType="str")
                    else:
                        # Run once the loop is exited
                        if port_choice == "0":
                            # Do nothing if user chooses to cancel
                            pass
                        else:
                            # Save the resulting valid port to config file
                            CONFIG_VARS["ARDUINO_PORT"] = port_choice
                            print(f"Saving new port '{port_choice}' to config file...")
                            AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,fileName=CONFIG_VARS["CONFIG_FILE_NAME"], directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
                case 4:
                    print("Change R&S instrument port")
                    # Check for available R&S instruments
                    available_instruments = INSTCONN.list_available_devices()
                    print(f"Current instrument is: {CONFIG_VARS['VNA_RESOURCE']}")
                    print(f"Here are the available instruments: {available_instruments}")

                    port_choice = str()
                    while (port_choice not in available_instruments and port_choice != "0"):
                        port_choice = AUXFN.get_user_choice(displayText="Enter a valid instrument resources ([0] to cancel): ", returnType="str")
                    else:
                        # Run once the loop is exited
                        if port_choice == "0":
                            # Do nothing if user chooses to cancel
                            pass
                        else:
                            # Save the resulting valid port to config file
                            CONFIG_VARS["VNA_RESOURCE"] = port_choice
                            print(f"Saving new instrument resource '{port_choice}' to config file...")
                            AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,fileName=CONFIG_VARS["CONFIG_FILE_NAME"], directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
                case _:
                    pass

            menu_choice = -1
        elif (menu_choice == 3):
            # Data Acquisition

            # Check for the status flag
            if (ARD_CONN_IS_READY == False) or (RSINST_CONN_IS_READY == False):
                print("ERROR Data acquisition cannot commence. One or more devices not initialised. Please initialise your devices before starting data acquisition.")
                continue

            # Start data acquisition process
            # Arduino
            ard_results_test = ARDCONN.get_FSR_vals(serialObject=serialObject, data_selection="voltage")
            print("DEBUG ard_results_test", ard_results_test)

            # R&S VNA
            inst_cal_status = bool()
            INSTCONN.vna_measurement_setup(instrument=RSINST, configVars=CONFIG_VARS)
            inst_cal_status = INSTCONN.calibrate_instrument(instrument=RSINST, configVars=CONFIG_VARS)
            vna_data = INSTCONN.acquire_vna_data(instrument=RSINST, configVars=CONFIG_VARS)
            print("DEBUG vna_data", vna_data)

            menu_choice = -1
        else:
            print("NOTICE: Exiting program...")
            exit()

    return

if __name__ == '__main__':
    main()