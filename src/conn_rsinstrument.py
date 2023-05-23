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
    # Start frequency
    instrument.write_str_with_opc(f'SENSe1:FREQuency:STARt {configVars["VNA_START_FREQ"]}MHz')
    # Stop frequency
    instrument.write_str_with_opc(f'SENSe1:FREQuency:STOP {configVars["VNA_STOP_FREQ"]}MHz')
    # Set number of sweep points to the defined number
    instrument.write_with_opc('SENSe1:SWEep:POINts ' + str(configVars["VNA_POINTS"]))
    # Set single sweep mode and stop acquisition
    instrument.write_str_with_opc("INIT1:CONT ON")
    return


def calibrate_instrument(instrument: RsInstrument.RsInstrument, configVars: dict):

    # https://github.com/Rohde-Schwarz/Examples/blob/main/VectorNetworkAnalyzers/Python/RsInstrument/RsInstrument_ZNB_CAL_P1_Save_Reload.py

    print("CALIBRATE: Calibration Started")
    vna_cal_kit_id = configVars["VNA_CAL_KIT_ID"]
    # Select cal kit
    instrument.write_str_with_opc(f'SENSe1:CORRection:CKIT:PC292:SELect "{vna_cal_kit_id}"')
    # Define gender of the port
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:CONN PC292MALE')
    # Choose OSM cal type
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:METHod:DEFine "NewCal", FOPort, 1')
    # Avoid to save the data to your default calibration
    instrument.write_str_with_opc('SENSe:CORRection:COLLect:ACQuire:RSAVe:DEFault OFF')

    confirmation_input = None
    # Open
    print("Please connect OPEN to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return False
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected OPEN, 1')
    confirmation_input = None
    # Short
    print("Please connect SHORT to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return False
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected SHORT, 1')
    confirmation_input = None
    # Load/Match
    print("Please connect MATCH/LOAD to port 1 and confirm by pressing '1': ")
    confirmation_input = int(input())
    if (confirmation_input != 1):
        print(f"You have entered {confirmation_input}. Returning back to menu.")
        return False
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:ACQuire:SELected MATCH, 1')
    confirmation_input = None

    calibration_name = "p1-glucoring.cal"
    print("CALIBRATE: Calibration done", "Applying calibration...")
    instrument.write_str_with_opc('SENSe1:CORRection:COLLect:SAVE:SELected')
    print(f"CALIBRATE: Saving calibration as {calibration_name}")
    instrument.write_str_with_opc(f'MMEMory:STORE:CORRection 1,"{calibration_name}"')
    return True


def acquire_vna_data(instrument: RsInstrument.RsInstrument, configVars: dict):
    """
    Gets the trace data and marker (min.) data from the VNA and processes it to provide magnitude, impedance etc.
    Args:
        instrument: The RsInstrument object that has already been initialised
        configVars: Configuration variables loaded from the configuration file

    Returns: A dict with `minpt_mag_dB`, `minpt_mag_phase`, `minpt_imp_real`, `minpt_imp_j`, `min_pt_freq`, `min_pt_mag`, `trace_data`
    """
    instrument.write_str_with_opc("CALCulate:MARKer1 ON")
    instrument.write_str_with_opc("CALCulate:MARKer1:X:SLIMits ON")
    instrument.write_str_with_opc("CALCulate:MARKer1:X:SLIMits:RIGHt 1.15GHz")
    instrument.write_str_with_opc("CALCulate:MARKer1:X:SLIMits:LEFT 750MHz")
    instrument.write_str_with_opc("CALCulate:MARKer1:MINimum:PEAK")

    instrument.write_str_with_opc("CALCulate:MARKer1:MODE RPDB") # Marker format of Magnitude in dB with Phase
    minpt_mag = str(znl.query_str_with_opc("CALC:MARK1:Y?")).split(",")
    instrument.write_str_with_opc("CALCulate:MARKer1:MODE IMPedance") # Market format of Impedance with real and imag.
    minpt_imp = str(znl.query_str_with_opc("CALC:MARK1:Y?")).split(",")

    minpt_mag_dB = minpt_mag[0]
    minpt_mag_phase = minpt_mag[1]
    minpt_imp_real = minpt_imp[0]
    minpt_imp_j = minpt_imp[1]

    instrument.write_str_with_opc("FORMat ASCii")
    trace_data = instrument.query_bin_or_ascii_float_list_with_opc("TRACe:DATA? TRACE1")
    print("DEBUG CH1 Trace Result Data is: ", data)
    min_pt_mag = min(trace_data)
    min_pt_freq = trace_data.index(min_pt_mag) / (xpoints - 1) * vna_bandwidth + vna_start_freq
    print(f"DEBUG min freq: {min_pt_freq}")

    return_data = {
        "minpt_mag_dB": minpt_mag_dB,
        "minpt_mag_phase": minpt_mag_phase,
        "minpt_imp_real": minpt_imp_real,
        "minpt_imp_j": minpt_imp_j,
        "min_pt_freq": min_pt_freq,
        "min_pt_mag": min_pt_mag,
        "trace_data": trace_data
    }
    return return_data