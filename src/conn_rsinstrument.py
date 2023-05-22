import RsInstrument

def list_available_devices():
    instrument_list = RsInstrument.RsInstrument.list_resources("?*")
    return instrument_list

def establish_connection(configVars: dict):
    instrument = RsInstrument.RsInstrument
    RSINST_CONN_IS_READY = False

    try:
        instrument = RsInstrument.RsInstrument(resource_name=configVars["VNA_RESOURCE"], id_query=True, reset=True, options="SelectVisa='rs', LoggingMode = Off, LoggingToConsole = False")

        instrument.visa_timeout = 5000
        instrument.opc_timeout = 5000
        instrument.clear_status()
        idn_response = instrument.query_str_with_opc("*IDN?")
        print(f"Connected to {idn_response}")
        RSINST_CONN_IS_READY = True
    except RsInstrument.ResourceError:
        print("ERROR! Instrument not found/unable to connect")
        RSINST_CONN_IS_READY = False
        return instrument, RSINST_CONN_IS_READY

    return instrument, RSINST_CONN_IS_READY

def vna_measurement_setup(instrument: RsInstrument.RsInstrument, configVars: dict):
    # Define all your measurement setups here
    instrument.write_str_with_opc("MEAS:PORT 1") # Select port 1
    instrument.write_str_with_opc("MEAS:FUNC:SEL S11") # Select S11 measurement
    instrument.write_str_with_opc("DISP:MAGN:Y:SPAC LOG") # Log space (dB) Y axis
    instrument.write_str_with_opc("DISP:MAGN:REF 0") # Set reference level at 0dB
    instrument.write_str_with_opc("DISP:MAGN:Y:SCAL 60") # Set the Y scale at 60 dB
    instrument.write_str_with_opc(f'SENSe1:FREQuency:STARt {configVars["VNA_START_FREQ"]}MHz')  # Start frequency
    instrument.write_str_with_opc(f'SENSe1:FREQuency:STOP {configVars["VNA_STOP_FREQ"]}MHz')  # Stop frequency
    instrument.write_with_opc('SENSe1:SWEep:POINts ' + str(configVars["VNA_POINTS"]))  # Set number of sweep points to the defined number
    instrument.write_str_with_opc("INIT1:CONT ON")  # Set single sweep mode and stop acquisition
def calibrate_equipment():
    pass

def acquire_vna_data(instrument: RsInstrument.RsInstrument, configVars: dict):
    pass

def write_vna_data():
    pass

# RESOURCE_STRING_USB = "USB::0x0AAD::0x0119::022019943::INSTR"  # USB-TMC (Test and Measurement Class)
# resource = 'TCPIP0::172.16.10.10::INSTR'  # ZNL VISA resource string for the device
# script_dir = os.path.dirname(__file__)
# output_folder = r'results'
# output_file = r'logfile.csv'  # Name and path of the logfile
# output_file_path = os.path.join(script_dir, output_folder, output_file)
# output_folder_path = os.path.join(script_dir, output_folder)
# points = 401  # Number of sweep points
# vna_start_freq = 750
# vna_stop_freq = 1150
# vna_bandwidth = vna_stop_freq - vna_start_freq
# cal_kit_id = "FSH-Z28"