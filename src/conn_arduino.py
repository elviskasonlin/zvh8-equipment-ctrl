#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 2023

@author: elviskasonlin
"""

import waiting
import serial
import time
def read_serial(serialObject):
    print("DEBUG I'm in read_serial")
    # print(serialObject)
    incoming_data = str()
    if serialObject.isOpen():
        try:
            serialObject.flush()
            incoming_data = serialObject.readline().decode(encoding="ascii").strip()
        except Exception as Error:
            print(Error)
    return incoming_data

def write_serial(write_data: str, serialObject):
    print("DEBUG I'm in write_serial")
    if serialObject.isOpen():
        try:
            serialObject.flush()
            serialObject.write(write_data.encode(encoding="ascii"))
        except Exception as error:
            print(error)

def poll_arduino(serialObject):
    initialisation_verify_data = "INIT:RXTX:SUC"
    initialisation_write_data = "INIT:RXTX:CHK\n"
    initialisation_read_data = str()

    write_serial(initialisation_write_data, serialObject)
    initialisation_read_data = read_serial(serialObject)

    if (initialisation_read_data == initialisation_verify_data):
        return True
    else:
        return False

    serialObject.reset_input_buffer()
    serialObject.reset_output_buffer()

def handshake_connection(serialObject, timeout: float, pollingRate: float):
    CONN_STATUS_FLAG = False

    try:
        CONN_STATUS_FLAG = waiting.wait(lambda:poll_arduino(serialObject), on_poll=lambda: print(f"Polling at the rate of {pollingRate}s. Waiting for Arduino until timeout of {timeout}s..."), timeout_seconds=timeout, sleep_seconds=1)
    except TimeoutExpired:
        print("Operation Timed Out! Unable to establish connection with Arduino")
        return False

    return CONN_STATUS_FLAG

def get_FSR_vals(serialObject: serial.Serial, data_selection: str):
    print("DEBUG I'm in get_FSR_vals")
    read_data = str()
    write_data = str()

    cmds = {
        "voltage": "INST:READ:VOL\n",
        "resistance": "INST:READ:RES\n",
        "force": "INST:READ:FOR\n",
        "all": "INST:READ:ALL\n"
    }

    # Ignore any invalid syntax error. Your inting system may not be updated. "Match" was added in python 3.10
    match data_selection:
        case "voltage":
            write_data = cmds["voltage"]
        case "resistance":
            write_data = cmds["resistance"]
        case "force":
            write_data = cmds["force"]
        case "all":
            write_data = cmds["all"]
        case _:
            write_data = cmds["all"]

    if serialObject.isOpen():
        try:
            serialObject.flushInput()
            serialObject.flushOutput()

            write_serial(write_data, serialObject)
            read_data = read_serial(serialObject)

        except Exception as err:
            print("Error! Error when writing and reading from Serial")
            print(err)

    return read_data

def current_time_ms():
    return round(time.time() * 1000)

def establish_connection(configVariables: dict):
    serial_parity = None
    match configVariables["ARDUINO_CONN_PARITY"]:
        case "E":
            serial_parity = serial.PARITY_EVEN
        case "O":
            serial_parity = serial.PARITY_ODD
        case _:
            serial_parity = serial.PARITY_NONE

    serialObject = serial.Serial(
            baudrate=configVariables["ARDUINO_BAUD"],
            port=configVariables["ARDUINO_PORT"],
            bytesize=serial.EIGHTBITS,
            parity=serial_parity,
            stopbits=serial.STOPBITS_ONE,
            timeout=configVariables["ARDUINO_CONN_TIMEOUT"],
            rtscts=True)

    # timeout of 0 is a non-blocking operation
    #start_time = current_time_ms()
    ARD_CONN_IS_READY = False
    ARD_CONN_IS_READY = handshake_connection(serialObject=serialObject, timeout=configVariables["ARDUINO_HSHK_TIMEOUT"], pollingRate=configVariables["ARDUINO_HSHK_POLLRATE"])

    # while True:
    #     if (((current_time_ms() - start_time) > configVariables["ARDUINO_HSHK_TIMEOUT"]) or ARD_CONN_IS_READY):
    #         break

    return serialObject, ARD_CONN_IS_READY
