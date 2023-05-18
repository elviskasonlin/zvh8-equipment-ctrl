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

import src.auxfn as AUXFN
import src.conn_arduino as ARDCONN
import src.conn_rsinstrument as INSTCONN

def main():

    menu_choice = -1
    while (menu_choice != 0):
        menu_choice = AUXFN.get_user_choice(displayText="Hello!", returnType="int")

        if (menu_choice == 1):
            # Device Initialisation

            # Initialise Devices
            ARDCONN.main()
            INSTCONN.main()
            # Check whether both devices are initialised by checking the status flags
            # Implement status flags
            print("All devices initialised")
            menu_choice = -1
        elif (menu_choice == 2):
            # Data Acquisition

            # Check for the status flag
            # Start data acquisition process
            menu_choice = -1
        elif (menu_choice == 2):
            # Settings

            # Set the settings required for initialisation
            # Set a default setting if no settings file is found

            menu_choice = -1
        else:
            pass

    return

if __name__ == '__main__':
    main()