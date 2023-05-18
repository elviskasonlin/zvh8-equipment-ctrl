#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 12:08:27 2023

@author: elviskasonlin
"""

import RsInstrument
import time
import os.path
import datetime

#
# Define variables
resource = 'TCPIP0::172.16.10.10::INSTR' # ZNL VISA resource string for the device
script_dir = os.path.dirname(__file__)
output_folder = r'results'
output_file = r'logfile.csv'  # Name and path of the logfile
output_file_path = os.path.join(script_dir, output_folder, output_file)
output_folder_path = os.path.join(script_dir, output_folder)
points = 401  # Number of sweep points
vna_start_freq = 750
vna_stop_freq = 1150
vna_bandwidth = vna_stop_freq - vna_start_freq
cal_kit_id = "FSH-Z28"

# Prepare instrument communication
znl = RsInstrument.RsInstrument(resource,
                   reset=True,
                   id_query=False,
                   options="SelectVisa='rs' , LoggingMode = Off, LoggingToConsole = False")

def comprep():
    """Preparation of the communication (termination, etc...)"""
    print(f'VISA Manufacturer: {znl.visa_manufacturer}')  # Confirm VISA package to be chosen
    znl.visa_timeout = 5000  # Timeout for VISA Read Operations
    znl.opc_timeout = 5000  # Timeout for opc-synchronised operations
    znl.clear_status()  # Clear status register

def close():
    """Close the VISA session"""
    znl.close()

def comcheck():
    """Check communication with the device"""
    # Just knock on the door to see if instrument is present
    idnresponse = znl.query_str_with_opc('*IDN?')
    #print('DEBUG Hello, I am ' + idnresponse)
    #print('DEBUG And I am equipped with the following options: ', znl.instrument_options)

def meassetup():
    """Assign additional settings to the channel"""
    #
    # Setup for CH1
    #
    znl.write_str_with_opc("MEAS:PORT 1") # Select port 1
    znl.write_str_with_opc("MEAS:FUNC:SEL S11") # Select S11 measurement
    znl.write_str_with_opc("DISP:MAGN:Y:SPAC LOG") # Log space (dB) Y axis
    znl.write_str_with_opc("DISP:MAGN:REF 0") # Set reference level at 0dB
    znl.write_str_with_opc("DISP:MAGN:Y:SCAL 60") # Set the Y scale at 60 dB
    znl.write_str_with_opc(f'SENSe1:FREQuency:STARt {vna_start_freq}MHz')  # Start frequency
    znl.write_str_with_opc(f'SENSe1:FREQuency:STOP {vna_stop_freq}MHz')  # Stop frequency
    znl.write_with_opc('SENSe1:SWEep:POINts '+str(points))  # Set number of sweep points to the defined number
    sleep(0.3)  # It will take some time to perform a complete sweep - wait for it
    znl.write_str_with_opc("INIT1:CONT ON")  # Set single sweep mode and stop acquisition

def calibrate_instrument():
    #https://github.com/Rohde-Schwarz/Examples/blob/main/VectorNetworkAnalyzers/Python/RsInstrument/RsInstrument_ZNB_CAL_P1_Save_Reload.py
    print("CALIBRATE: Calibration Started")
    znl.write_str_with_opc(f'SENSe1:CORRection:CKIT:PC292:SELect "{cal_kit_id}"')  # Select cal kit
    znl.write_str_with_opc('SENSe1:CORRection:COLLect:CONN PC292MALE')  # Define gender of the port
    znl.write_str_with_opc('SENSe1:CORRection:COLLect:METHod:DEFine "NewCal", FOPort, 1')  # Choose OSM cal type
    znl.write_str_with_opc('SENSe:CORRection:COLLect:ACQuire:RSAVe:DEFault OFF')  # Avoid to save the data to your default calibration

    confirmation_input = None
    # Open
    print("Please connect OPEN to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return
    znl.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected OPEN, 1')
    confirmation_input = None
    # Short
    print("Please connect SHORT to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return
    znl.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected SHORT, 1')
    confirmation_input = None
    # Load/Match
    print("Please connect MATCH/LOAD to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return
    znl.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected MATCH, 1')
    confirmation_input = None

    print("CALIBRATE: Calibration done")
    print("CALIBRATE: Saving calibration data")

def save_inst_calibration():
    pass

def load_inst_calibration():
    pass

def filewrite():

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    logfile = open(output_file_path, "w")  # Create logfile

    logfile.write("Timestamp / HH:MM:SS.SS, Sweep points / #, Freq / Hz, Mag. / db, Impedence / Ohm")   # Write table headline
    logfile.write("\n")

    xpoints = znl.query_int('SENSe1:SWEep:POINts?')  # Request number of frequency points
    #print(f'DEBUG The current trace contains {xpoints} frequency points')

    znl.write_str_with_opc("CALCulate:MARKer1 ON")
    znl.write_str_with_opc("CALCulate:MARKer1:X:SLIMits ON")
    znl.write_str_with_opc("CALCulate:MARKer1:X:SLIMits:RIGHt 1.15GHz")
    znl.write_str_with_opc("CALCulate:MARKer1:X:SLIMits:LEFT 750MHz")
    znl.write_str_with_opc("CALCulate:MARKer1:MINimum:PEAK")

    znl.write_str_with_opc("CALCulate:MARKer1:MODE RPDB") # Marker format of Magnitude in dB with Phase
    minpt_mag = str(znl.query_str_with_opc("CALC:MARK1:Y?")).split(",")
    znl.write_str_with_opc("CALCulate:MARKer1:MODE IMPedance") # Market format of Impedence with real and imag.
    minpt_imp = str(znl.query_str_with_opc("CALC:MARK1:Y?")).split(",")

    minpt_mag_dB = minpt_mag[0]
    minpt_mag_phase = minpt_mag[1]
    minpt_imp_real = minpt_imp[0]
    minpt_imp_j = minpt_imp[1]

    znl.write_str_with_opc("FORMat ASCii")
    data = znl.query_bin_or_ascii_float_list_with_opc("TRACe:DATA? TRACE1")
    print("DEBUG CH1 Trace Result Data is: ", data)
    min_pt_mag = min(data)
    min_pt_freq = data.index(min_pt_mag) / (xpoints - 1) * vna_bandwidth + vna_start_freq
    print(f"DEBUG min freq: {min_pt_freq}")

    logfile.write(str(datetime.datetime.now()) + ",")
    logfile.write(str(xpoints) + ",")
    logfile.write(str(min_pt_freq) + ",")
    logfile.write(minpt_mag_dB + ",")
    logfile.write(minpt_imp_real + "(" + minpt_imp_j + ")" + "\n")

    logfile.close()
    print("I'm done. Data is written to ", output_file_path)

def main():
    comprep()
    comcheck()
    meassetup()
    filewrite()
    close()

main()