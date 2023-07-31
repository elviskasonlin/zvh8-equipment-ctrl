#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instrumentation control and data acquisition script
For use in collecting the data from both the Vector Network Analyser and the Arduino (that is connected to force-sensing resistors)
Currently implemented for Rohde and Schwarz ZVH8 Cable and Antenna Analyser and Arduino Uno (5V)

Version Release 1.0

Created on Tue May 16 17:32:29 2023
@author: elviskasonlin
"""
import datetime
import time

import serial.tools.list_ports

import src.aux_fns as AUXFN
import src.conn_arduino as ARDCONN
import src.conn_rsinstrument as INSTCONN
import src.gui as GUI
import src.rw_data as RWDATA
import src.calculate as TRACECALC
import src.plotter as PLOTTER

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
            print(f"INITIALISE Establishing connection with Arduino at {CONFIG_VARS['ARDUINO_PORT']}...")
            if not ARD_CONN_IS_READY:
                serialObject, ARD_CONN_IS_READY = ARDCONN.establish_connection(configVariables=CONFIG_VARS)
                if (ARD_CONN_IS_READY == True):
                   print(f"SUCCESS Connected to {CONFIG_VARS['ARDUINO_PORT']}")
            else:
                print("WARNING Arduino already connected")
            #print("DEBUG Arduino Connection Status:", ARD_CONN_IS_READY)

            # Initialise R&S VNA
            print("INITIALISE Establishing connection with VNA...")
            if not RSINST_CONN_IS_READY:
                RSINST, RSINST_CONN_IS_READY = INSTCONN.establish_connection(configVars=CONFIG_VARS)
                if (RSINST_CONN_IS_READY == True):
                    print(f"SUCCESS Connected to {CONFIG_VARS['VNA_RESOURCE']}")
            else:
                print("WARNING VNA already connected")
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
                    print("WARNING VNA uncalibrated. You can run through the calibration routine from settings")
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
                case 5:
                    print(f"Resetting config. file with default configuration...")
                    CONFIG_VARS = copy.deepcopy(DEFAULT_CONFIG_VARS)
                    AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR, fileName=CONFIG_VARS["CONFIG_FILE_NAME"],
                                             directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
                    print(f"DONE Configuration file reset!")
                case 6:
                    print("Entering VNA calibration routine")
                    if RSINST is None:
                        print("ERROR No valid instruments found")
                        continue
                    else:
                        inst_cal_status = INSTCONN.calibrate_instrument(instrument=RSINST, configVars=CONFIG_VARS)
                        if inst_cal_status == True:
                            print("CALIBRATION Calibration successful")
                        else:
                            print("CALIBRATION Calibration unsuccessful")
                case 7:
                    if RSINST is None:
                        print("ERROR No valid instruments found")
                        continue
                    else:
                        print(f"Saving VNA state to {CONFIG_VARS['VNA_STATE_FILE']}")
                        INSTCONN.store_calibration(instrument=RSINST, cal_name=CONFIG_VARS["VNA_STATE_FILE"])
                case 8:
                    if RSINST is None:
                        print("ERROR No valid instruments found")
                        continue
                    else:
                        print(f"Attempting to load VNA state from {CONFIG_VARS['VNA_STATE_FILE']}")
                        INSTCONN.load_calibration(instrument=RSINST, cal_name=CONFIG_VARS["VNA_STATE_FILE"])
                case 9:
                    new_freq_start = AUXFN.get_user_input(display_text="Enter start frequency in MHz: ", return_type="int")
                    new_freq_stop = AUXFN.get_user_input(display_text="Enter stop frequency in MHz: ", return_type="int")
                    if (new_freq_start <= 8000 and new_freq_start >= 1) and (new_freq_stop <= 8000 and new_freq_stop >= 1) and (new_freq_stop > new_freq_start):
                        CONFIG_VARS["VNA_START_FREQ"] = new_freq_start
                        CONFIG_VARS["VNA_STOP_FREQ"] = new_freq_stop
                        AUXFN.save_configuration(currentWorkingDir=CURRENT_WORKING_DIR, fileName=CONFIG_VARS["CONFIG_FILE_NAME"], directoryName=CONFIG_VARS["CONFIG_FOLDER"], configData=CONFIG_VARS)
                        print("NOTICE Configuration saved with new start and stop frequencies")
                        print("NOTICE Setting measurement again...")
                        INSTCONN.vna_measurement_setup(instrument=RSINST, configVars=CONFIG_VARS)
                        print("SUCCESS VNA configured with new measurement settings")
                    else:
                        print("ERROR Unable to complete changes in start and stop frequencies. Are the start and stop frequencies valid?")
                case 10:
                    try:
                        print("Reloading configuration from file...")
                        CONFIG_VARS = AUXFN.load_configuration(currentWorkingDir=CURRENT_WORKING_DIR, fileName=DEFAULT_CONFIG_VARS["CONFIG_FILE_NAME"],directoryName=DEFAULT_CONFIG_VARS["CONFIG_FOLDER"])
                        print("SUCCESS Configuration reloaded")
                    except Exception as err:
                        print(f"ERROR Cannot reload configuration with the following error message: {err}")
                case _:
                    pass

            menu_choice = -1
        elif menu_choice == 3:
            # Data Acquisition

            # Check for the status flag
            if (ARD_CONN_IS_READY == False) or (RSINST_CONN_IS_READY == False):
                print("ERROR Data acquisition cannot commence. One or more devices not initialised. Please initialise your devices before starting data acquisition.")
                continue

            original_output_file_name = copy.deepcopy(CONFIG_VARS["OUTPUT_FILE_NAME"])

            to_automate_daq = False
            daq_cycles = 5
            daq_cycle_count = 0
            to_automate_daq = AUXFN.get_user_input(display_text="QUERY Is this an automated run based on set cycles without manual confirmation? [Y]es [N]o: ", return_type="bool")
            daq_cycles = AUXFN.get_user_input(display_text="Enter the number of cycles you would like to run the acquisition process for: ", return_type="int")
            reading_delay = AUXFN.get_user_input(display_text="Enter the delay between readings in seconds: ", return_type="float")
            fname_suffix = AUXFN.get_user_input(display_text="(Optional) File name suffix if any. Leave blank if none:", return_type="str")

            print(f"DAQ You have chosen the following options: daq automation = {str(to_automate_daq)}, daq cycles = {str(daq_cycles)}, delay time = {str(reading_delay)}, file name suffix = {fname_suffix}")
            choice_confirmed = AUXFN.get_user_input(display_text="Confirm choice? [Y]es [N]o: ", return_type="bool")

            if not choice_confirmed:
                continue

            # Initialise results save file
            field_names = CONFIG_VARS["FIELD_NAMES"]
            current_time_for_file_naming = datetime.datetime.now().timetuple()
            file_timestamp = f"{current_time_for_file_naming[0]}{current_time_for_file_naming[1]}{current_time_for_file_naming[2]}{current_time_for_file_naming[3]}{current_time_for_file_naming[4]}{current_time_for_file_naming[5]}"
            CONFIG_VARS["OUTPUT_FILE_NAME"] = CONFIG_VARS["OUTPUT_FILE_NAME"] + "-" + fname_suffix
            # print("DEBUG file_timestamp", file_timestamp)
            RWDATA.initialise_results_file(config_vars=CONFIG_VARS, field_names=field_names, timestamp=file_timestamp)

            write_buffer_default = {
                field_names[0]: None,
                field_names[1]: None,
                field_names[2]: None,
                field_names[3]: None,
                field_names[4]: None,
                field_names[5]: None,
                field_names[6]: None,
                field_names[7]: None,
                field_names[8]: None,
                field_names[9]: None,
                field_names[10]: None,
                field_names[11]: None,
                field_names[12]: None
            }
            write_single_buffer = dict(write_buffer_default)
            write_big_buffer = []

            daq_start_time = datetime.datetime.now()
            while daq_cycle_count < daq_cycles:
                # Start data acquisition process
                # R&S VNA
                vna_data = INSTCONN.acquire_vna_data(instrument=RSINST, configVars=CONFIG_VARS)
                # print("DEBUG vna_data", vna_data)
                # Arduino
                ard_results_vol, ard_read_status = ARDCONN.get_FSR_vals(serialObject=serialObject, data_selection="voltage")
                # print("DEBUG ard_results_vol", ard_results_vol, "ard_read_status:", ard_read_status)
                ard_results_res, ard_read_status = ARDCONN.get_FSR_vals(serialObject=serialObject, data_selection="resistance")
                # print("DEBUG ard_results_res", ard_results_res, "ard_read_status:", ard_read_status)

                current_daq_process_time = datetime.datetime.now()
                current_daq_process_time_delta = current_daq_process_time - daq_start_time
                data_timestamp = current_daq_process_time_delta.total_seconds()
                print(f"NOTICE Reading {daq_cycle_count + 1} taken at timestamp", data_timestamp)
                print(f"Arduino with status {ard_read_status} has data read: voltage = {ard_results_vol} and resistance = {ard_results_res}")

                # Process trace data
                #"Cutoff Mag / dB", "Bandwidth / MHz", "Q Factor at Cutoff Mag"
                target_cutoff_mags = [-10, -6, -3]
                processed_trace_results = TRACECALC.get_trace_analysis(target_cutoff_mags=target_cutoff_mags,
                                                                       sweep_start_f=CONFIG_VARS["VNA_START_FREQ"],
                                                                       sweep_stop_f=CONFIG_VARS["VNA_STOP_FREQ"],
                                                                       trace_data=vna_data["trace_data"])

                # Save to buffer
                write_single_buffer[field_names[0]] = data_timestamp
                write_single_buffer[field_names[1]] = CONFIG_VARS["VNA_POINTS"]
                write_single_buffer[field_names[2]] = vna_data["min_pt_freq"]
                write_single_buffer[field_names[3]] = vna_data["min_pt_mag"]
                write_single_buffer[field_names[4]] = f'{vna_data["minpt_imp_real"]}+j{vna_data["minpt_imp_j"]}'
                write_single_buffer[field_names[5]] = vna_data["trace_data"]
                write_single_buffer[field_names[6]] = ard_results_res
                write_single_buffer[field_names[7]] = ard_results_vol
                write_single_buffer[field_names[8]] = processed_trace_results["cutoff_mag"]
                write_single_buffer[field_names[9]] = processed_trace_results["bandwidth"]
                write_single_buffer[field_names[10]] = processed_trace_results["q_factor"]
                write_single_buffer[field_names[11]] = CONFIG_VARS["VNA_START_FREQ"]
                write_single_buffer[field_names[12]] = CONFIG_VARS["VNA_STOP_FREQ"]
                write_big_buffer.append(copy.deepcopy(write_single_buffer))
                write_single_buffer.update(write_buffer_default)
                daq_cycle_count += 1

                if to_automate_daq:
                    time.sleep(reading_delay)
                else:
                    to_continue_process = AUXFN.get_user_input(display_text="Continue next reading? [Y]es [N]o: ", return_type="bool")
                    if to_continue_process:
                        continue
                    else:
                        break
            else:
                print("DAQ Data acqusition process complete. Now writing the data...")
                # print("DEBUG Data inside the big buffer:", write_big_buffer)
                RWDATA.write_operation(config_vars=CONFIG_VARS, data=write_big_buffer, field_names=field_names, timestamp=file_timestamp)

            print(f"DAQ Data acquisition and writing process completed with {daq_cycles} cycles!")

            # Reset the output file name
            CONFIG_VARS["OUTPUT_FILE_NAME"] = original_output_file_name
            menu_choice = -1
        elif menu_choice == 4:
            # Enter plotting function
            PLOTTER.engage_plotter(config_vars=CONFIG_VARS)
        else:
            print("NOTICE: Exiting program...")
            exit()

    return


if __name__ == '__main__':
    main()