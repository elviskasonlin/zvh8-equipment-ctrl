import RsInstrument
import pyvisa.errors

import src.aux_fns as AUXFN

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
        print(f"Device connected to is {idn_response}")
        RSINST_CONN_IS_READY = True
    except (RsInstrument.ResourceError, pyvisa.errors.VisaIOError):
        print("ERROR! Instrument VNA not found/unable to connect")
        RSINST_CONN_IS_READY = False
        return instrument, RSINST_CONN_IS_READY
    except  RsInstrument.TimeoutException:
        print("ERROR! Timed out when connection to the VNA")
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


#     zna.write_str_with_opc('MMEMORY:STORE:CORRection 1, "AUTOCAL.cal"')  # Save current calibration
#     zna.write_str_with_opc('MMEMORY:LOAD:CORRection 1, "AUTOCAL.cal"')  # And reload it (just to show the command)
def load_calibration():
    pass

def store_calibration():
    pass

def calibrate_instrument(instrument: RsInstrument.RsInstrument, configVars: dict):

    # https://github.com/Rohde-Schwarz/Examples/blob/main/VectorNetworkAnalyzers/Python/RsInstrument/RsInstrument_ZNB_CAL_P1_Save_Reload.py

    instrument_cal_status = instrument.query_str_with_opc("CAL:MODE?")
    print(instrument_cal_status)

    current_status = str()
    user_input = str()

    if instrument_cal_status != 1:
        current_status = instrument.query_str_with_opc("CALibration:STARt? S11Cal")
        while (current_status != "Calibration done" and user_input != 0):
            print("CALIBRATE", current_status)
            user_input = AUXFN.get_user_input(display_text="Input (Confirm by pressing [1], Cancel by pressing [0]:", return_type="int")
            if user_input == 0:
                print("CALIBRATE Aborting calibration")
                instrument.write_str_with_opc("CALibration:ABORt")
                return False
            else:
                if (current_status != "Calibration done"):
                    current_status = instrument.query_str_with_opc("CAL:CONT?")
                continue
        return True
    else:
        print("CALIBRATE This measurement is already calibrated")

    return


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
    minpt_mag = str(instrument.query_str_with_opc("CALC:MARK1:Y?")).split(",")
    instrument.write_str_with_opc("CALCulate:MARKer1:MODE IMPedance") # Market format of Impedance with real and imag.
    minpt_imp = str(instrument.query_str_with_opc("CALC:MARK1:Y?")).split(",")

    minpt_mag_dB = minpt_mag[0]
    minpt_mag_phase = minpt_mag[1]
    minpt_imp_real = minpt_imp[0]
    minpt_imp_j = minpt_imp[1]

    instrument.write_str_with_opc("FORMat ASCii")
    trace_data = instrument.query_bin_or_ascii_float_list_with_opc("TRACe:DATA? TRACE1")
    #print("DEBUG CH1 Trace Result Data is: ", trace_data)
    vna_bandwidth = configVars["VNA_STOP_FREQ"] - configVars["VNA_START_FREQ"]
    min_pt_mag = min(trace_data)
    min_pt_freq = trace_data.index(min_pt_mag) / (configVars["VNA_POINTS"] - 1) * vna_bandwidth + configVars["VNA_START_FREQ"]
    #print(f"DEBUG min freq: {min_pt_freq}")

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