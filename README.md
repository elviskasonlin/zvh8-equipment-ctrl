# CLI Program for Instrumentation Control of R&S ZVH8 VNA

This program features automated data acquisition & data extraction, S11 parameters calculation against a target dB value, and trace & insight plotting through an easy-to-use command line interface. Created for use in one SUTD EPD's research projects for characterisation of an antenna-based sensor. This program communicates with a Rohde & Schwarz ZVH8 Antenna and Cable Analyzer through the PyVISA package (or rather, "RsInstrument" a R&amp;S implementation). 

## Quirks to note
There are few quirks/issues that is inherently present.

* You must run the python program first if a config file is not present
* Not all configuration can be changed through the "settings" menu in the CLI
* ZVH8 communication via USB and resource string issue
  * You *must* use the string "TCPIP0::172.16.10.10::INSTR" when connecting to the unit. No other resources will work.
  * The R&S VISA tester cannot find any resources even if the ZVH8 is connected. But it will work if you use the resource string stated above
* VNA calibration step upon establishing connection
  * The current code as released will ask you to do a 1-port VNA calibration upon successful connection
  * If you already have a saved VNA calibrated state/setting previously (it saves to the default "CTRL_CAL_STATE.SET"; can be changed in config), skip this and then manually load by going to the "settings" menu and selecting "load VNA state"
