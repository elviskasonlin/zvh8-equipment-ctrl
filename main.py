#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instrumentation control and data acquisition script
For use in collecting the data from both the Vector Network Analyser and the Arduino (that is connected to force-sensing resistors)
Currently implemented for Rohde and Schwarz ZVH8 Cable and Antenna Analyser and Arduino Uno (5V)

Version Alpha 2.0

Created on Tue May 16 17:32:29 2023
@author: elviskasonlin
"""
import datetime

import serial.tools.list_ports

import src.aux_fns as AUXFN
import src.conn_arduino as ARDCONN
import src.conn_rsinstrument as INSTCONN
import src.gui as GUI
import src.save_data as SAVEDATA

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

    while menu_choice != 0:
        print(GUI.get_menu_text(menuName="main_menu"))
        menu_choice = AUXFN.get_user_input(display_text="Input: ", return_type="int")

        if menu_choice == 1:
            # Device Initialisation

            # Initialise Arduino Serial
            CONFIG_VARS["ARDUINO_PORT"] = "COM3"
            print("INITIALISE Establishing connection with Arduino...")
            serialObject, ARD_CONN_IS_READY = ARDCONN.establish_connection(configVariables=CONFIG_VARS)
            if (ARD_CONN_IS_READY == True):
                print(f"SUCCESS Connected to {CONFIG_VARS['ARDUINO_PORT']}")
            #print("DEBUG Arduino Connection Status:", ARD_CONN_IS_READY)

            # Initialise R&S VNA
            print("INITIALISE Establishing connection with VNA...")
            RSINST, RSINST_CONN_IS_READY = INSTCONN.establish_connection(configVars=CONFIG_VARS)
            if (RSINST_CONN_IS_READY == True):
                print(f"SUCCESS Connected to {CONFIG_VARS['VNA_RESOURCE']}")
            #print("DEBUG RS Inst. Connection Status:", RSINST_CONN_IS_READY)

            if (ARD_CONN_IS_READY == False) or (RSINST_CONN_IS_READY == False):
                print("INITIALISE Failed to initialise one or more devices. Please check your connections and try again")
            else:
                inst_cal_status = bool()
                if RSINST_CONN_IS_READY == True:
                    print("INITIALISE Setting up VNA measurement settings...")
                    INSTCONN.vna_measurement_setup(instrument=RSINST, configVars=CONFIG_VARS)
                    inst_cal_status = INSTCONN.calibrate_instrument(instrument=RSINST, configVars=CONFIG_VARS)
                print("SUCCESS All devices initialised")
                if inst_cal_status != True:
                    print("WARNING But device was not calibrated")
            menu_choice = -1
        elif menu_choice == 2:
            # Settings
            # Set the settings required for initialisation
            # Set a default setting if no settings file is found

            print(GUI.get_menu_text(menuName="settings_menu"))
            menu_choice = AUXFN.get_user_input(display_text="Input: ", return_type="int")
            match menu_choice:
                case 1:
                    print("Change save folder name")
                    print(f"Current save folder name is: {CONFIG_VARS['OUTPUT_FOLDER']}")

                    choice, fname = str(), str()
                    while (fname != "C"):
                        fname = AUXFN.get_user_input(display_text="Change folder name to ([C] to cancel): ", return_type="str").strip()
                        print("DEBUG", fname)
                        if (fname == "C"):
                            print("Returning back to menu...")
                            break
                        choice = AUXFN.get_user_input(display_text=f"You have entered `{fname}`, confirm? [Y]es [N]o: ", return_type="bool")
                        match choice:
                            case True:
                                print("Updating configuration file with new output folder name...")
                                CONFIG_VARS["OUTPUT_FOLDER"] = fname
                                AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,
                                                         fileName=CONFIG_VARS["CONFIG_FILE_NAME"],
                                                         directoryName=CONFIG_VARS["CONFIG_FOLDER"],
                                                         configData=CONFIG_VARS)
                                break
                            case False:
                                continue
                            case _:
                                print("An invalid entry, please try again")
                                continue
                case 2:
                    print("Change save file name")
                    print(f"Current save file name is: {CONFIG_VARS['OUTPUT_FILE_NAME']}")

                    choice, fname = str(), str()
                    while (fname != "C"):
                        fname = AUXFN.get_user_input(display_text="Change file name to ([C] to cancel): ", return_type="str")
                        if (fname == "C"):
                            print("Returning back to menu...")
                            break
                        choice = AUXFN.get_user_input(display_text=f"You have entered `{fname}`, confirm? [Y]es [N]o: ", return_type="bool")
                        match choice:
                            case True:
                                print("Updating configuration file with new output file name...")
                                CONFIG_VARS["OUTPUT_FILE_NAME"] = fname
                                AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR,
                                                         fileName=CONFIG_VARS["CONFIG_FILE_NAME"],
                                                         directoryName=CONFIG_VARS["CONFIG_FOLDER"],
                                                         configData=CONFIG_VARS)
                                break
                            case False:
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
                    while (port_choice not in available_serial_dvcs_in_strlist) and (port_choice != "C"):
                        port_choice = AUXFN.get_user_input(display_text="Enter a valid port path ([C] to cancel): ", return_type="str")
                    else:
                        # Run once the loop is exited
                        if port_choice == "C":
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
                    while (port_choice not in available_instruments) and (port_choice != "C"):
                        port_choice = AUXFN.get_user_input(display_text="Enter a valid instrument resources ([C] to cancel): ", return_type="str")
                    else:
                        # Run once the loop is exited
                        if port_choice == "C":
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
        elif menu_choice == 3:
            # Data Acquisition

            # Check for the status flag
            # if (ARD_CONN_IS_READY == False) or (RSINST_CONN_IS_READY == False):
            #     print("ERROR Data acquisition cannot commence. One or more devices not initialised. Please initialise your devices before starting data acquisition.")
            #     continue

            to_automate_daq = False
            daq_cycles = 5
            daq_cycle_count = 0
            to_automate_daq = AUXFN.get_user_input(display_text="QUERY Is this an automated run based on set cycles without manual confirmation? [Y]es [N]o: ", return_type="bool")
            daq_cycles = AUXFN.get_user_input(display_text="Enter the number of cycles you would like to run the acquisition process for: ", return_type="int")

            print(f"DAQ You have chosen the following options: daq automation = {str(to_automate_daq)}, daq cycles = {str(daq_cycles)}")
            choice_confirmed = AUXFN.get_user_input(display_text="Confirm choice? [Y]es [N]o: ", return_type="bool")

            if not choice_confirmed:
                continue

            field_names = ["Timestamp / HH:MM:SS.SS", "Sweep points / #", "Freq / Hz", "Mag. / dB", "Impedence / Ohm", "Trace Data", "FSR Resistance / Ohm", "FSR Voltage / V"]
            current_time = datetime.datetime.now().timetuple()
            file_timestamp = f"{current_time[0]}{current_time[1]}{current_time[2]}{current_time[3]}{current_time[4]}{current_time[5]}"
            print("DEBUG file_timestamp", file_timestamp)
            SAVEDATA.initialise_results_file(config_vars=CONFIG_VARS, field_names=field_names, timestamp=file_timestamp)

            write_single_buffer = {
                "Timestamp / HH:MM:SS.SS": 1,
                "Sweep points / #": 1,
                "Freq / Hz": 1 ,
                "Mag. / dB": 1,
                "Impedence / Ohm": 1,
                "Trace Data": 1,
                "FSR Resistance / Ohm": 1,
                "FSR Voltage / V": 1
            }
            write_big_buffer = []

            while daq_cycle_count < daq_cycles:
                # Start data acquisition process
                # R&S VNA
                # vna_data = INSTCONN.acquire_vna_data(instrument=RSINST, configVars=CONFIG_VARS)
                # print("DEBUG vna_data", vna_data)
                # # Arduino
                # ard_results_vol, ard_read_status = ARDCONN.get_FSR_vals(serialObject=serialObject, data_selection="voltage")
                # print("DEBUG ard_results_vol", ard_results_test, "ard_read_status:", ard_read_status)
                # ard_results_res, ard_read_status = ARDCONN.get_FSR_vals(serialObject=serialObject, data_selection="resistance")
                # print("DEBUG ard_results_res", ard_results_test, "ard_read_status:", ard_read_status)

                data_timestamp = str(datetime.datetime.now())
                write_single_buffer["Timestamp / HH:MM:SS.SS"] = data_timestamp
                write_single_buffer["Sweep points / #"] = 1
                write_single_buffer["Freq / Hz"] = 1
                write_single_buffer["Mag. / dB"] = 1
                write_single_buffer["Impedence / Ohm"] = 1
                write_single_buffer["Trace Data"] = 1
                write_single_buffer["FSR Resistance / Ohm"] = 1
                write_single_buffer["FSR Voltage / V"] = 1
                write_big_buffer.append(write_single_buffer)
                daq_cycle_count += 1
            else:
                print("DAQ Data acqusition process complete. Now writing the data...")
                SAVEDATA.write_operation(config_vars=CONFIG_VARS, data=write_big_buffer, field_names=field_names, timestamp=file_timestamp)

            print(f"DAQ Data acquisition and writing process completed with {daq_cycles} cycles!")

            menu_choice = -1
        else:
            print("NOTICE: Exiting program...")
            exit()

    return


if __name__ == '__main__':
    main()