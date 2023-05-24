#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 2023

@author: elviskasonlin
"""

import waiting
import serial
import time


def read_serial(serialObject: serial.Serial):
    """
    Serial reads from the Arduino. Written on top of the .readline function to include decoding and formatting.
    Args:
        serialObject (`serial.Serial`): The serial object

    Returns:

    """
    # print("DEBUG I'm in read_serial")
    # print(serialObject)
    incoming_data = str()
    if serialObject.isOpen():
        try:
            serialObject.flush()
            incoming_data = serialObject.readline().decode(encoding="ascii").strip()
            # print("DEBUG Incoming data: ", incoming_data)
        except Exception as Error:
            print(Error)
    return incoming_data


def write_serial(write_data: str, serialObject: serial.Serial):
    """
    Serial writes to the Arduino. Written on top of the .write function to include encoding and checks like whether the Serial Port is open and to wait for any previous write operations to complete.
    Args:
        write_data (`str`): The data to write to arduino
        serialObject (`serial.Serial`): The serial object
    """
    # print("DEBUG I'm in write_serial")
    if serialObject.isOpen():
        try:
            serialObject.flush()
            serialObject.write(write_data.encode(encoding="ascii"))
        except Exception as error:
            print(error)


def poll_arduino(serialObject: serial.Serial):
    """
    A function that will poll the arduino with a handshaking call & response during the connection handshaking process. Will verify whether the response matches the expected response.

    Args:
        serialObject (`serial.Serial`): The serial object

    Returns:
        (`Bool`): True if the handshaking is successful and False if it is not

    """
    initialisation_verify_data = "INIT:RXTX:SUC"
    initialisation_write_data = "INIT:RXTX:CHK\n"
    initialisation_read_data = str()

    write_serial(initialisation_write_data, serialObject)
    initialisation_read_data = read_serial(serialObject)

    if (initialisation_read_data == initialisation_verify_data):
        serialObject.reset_input_buffer()
        serialObject.reset_output_buffer()
        return True
    else:
        serialObject.reset_input_buffer()
        serialObject.reset_output_buffer()
        return False


def handshake_connection(serialObject: serial.Serial, timeout: float, pollingRate: float):
    """
    Used for initial handshaking between this script and arduino
    Args:
        serialObject (`serial.Serial`): The serial object
        timeout (`float`): The timeout duration in seconds
        pollingRate (`float`): The polling rate in seconds. Should be less than the timeout duration

    Returns:
         (`bool`) Whether the connection is successful
    """
    conn_status_flag = False

    try:
        conn_status_flag = waiting.wait(lambda:poll_arduino(serialObject), on_poll=lambda: print(f"Polling at the rate of {pollingRate}s. Waiting for Arduino until timeout of {timeout}s..."), timeout_seconds=timeout, sleep_seconds=pollingRate)
    except TimeoutExpired:
        print("Operation Timed Out! Unable to establish connection with Arduino")
    return conn_status_flag


def poll_arduino_reading(serialObject: serial.Serial):
    read_data = read_serial(serialObject)
    if (read_data != ""):
        return read_data


def get_FSR_vals(serialObject: serial.Serial, data_selection: str):
    """
    Gets the force-sensing resistor values from the Arduino and returns them as a string of values

    Args:
        serialObject (`serial.Serial`): The serial object
        data_selection (`str`): Which data you would like from the FSR. Valid options are "voltage", "resistance", "force", and "all"

    Returns: (`str`, `bool`) data and whether the connection was successful. If unsuccessful, `"", False`

    """
    # print("DEBUG I'm in get_FSR_vals")
    read_data = str()
    write_data = str()

    cmds = {
        "voltage": "INST:READ:VOL\n",
        "resistance": "INST:READ:RES\n",
        "force": "INST:READ:FOR\n",
        "all": "INST:READ:ALL\n"
    }

    match data_selection:
        case "voltage" | "vol":
            write_data = cmds["voltage"]
        case "resistance" | "res":
            write_data = cmds["resistance"]
        case "force" | "for":
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
            read_data = ""
            try:
                pollingRate = 0.1
                timeout = 1.0
                read_data = waiting.wait(lambda: poll_arduino_reading(serialObject=serialObject), timeout_seconds=timeout, sleep_seconds=pollingRate)
            except waiting.exceptions.TimeoutExpired:
                print("Operation Timed Out! Unable to get any results from Arduino")
                return read_data, False
            # print("DEBUG: FSR read_data:", read_data)
        except Exception as err:
            print("Error! Error when writing and reading from Serial")
            print(err)
            return read_data, False
    return read_data, True


def current_time_ms():
    return round(time.time() * 1000)


def establish_connection(configVariables: dict):
    ard_conn_is_ready = False

    serial_parity = None
    serial_object = None

    match configVariables["ARDUINO_CONN_PARITY"]:
        case "E":
            serial_parity = serial.PARITY_EVEN
        case "O":
            serial_parity = serial.PARITY_ODD
        case _:
            serial_parity = serial.PARITY_NONE

    try:
        serial_object = serial.Serial(
                baudrate=configVariables["ARDUINO_BAUD"],
                port=configVariables["ARDUINO_PORT"],
                bytesize=serial.EIGHTBITS,
                parity=serial_parity,
                stopbits=serial.STOPBITS_ONE,
                timeout=configVariables["ARDUINO_CONN_TIMEOUT"],
                rtscts=True)
    except serial.SerialException as err:
        print("ERROR! Unable to connect to the Arduino. Are you sure the Arduino is connected and its connection port is specified correctly?")
        ard_conn_is_ready = False
        return serial_object, ard_conn_is_ready


    # timeout of 0 is a non-blocking operation
    #start_time = current_time_ms()
    ard_conn_is_ready = handshake_connection(serialObject=serial_object, timeout=configVariables["ARDUINO_HSHK_TIMEOUT"], pollingRate=configVariables["ARDUINO_HSHK_POLLRATE"])

    # while True:
    #     if (((current_time_ms() - start_time) > configVariables["ARDUINO_HSHK_TIMEOUT"]) or ARD_CONN_IS_READY):
    #         break

    return serial_object, ard_conn_is_ready
