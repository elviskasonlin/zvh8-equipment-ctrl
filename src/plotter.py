#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 2023

@author: elviskasonlin
"""

import src.rw_data as RWDATA
import src.aux_fns as AUXFN
import src.calculate as CALC
import numpy
import scipy
import matplotlib as plt


def engage_plotter(config_vars: dict):
    files = RWDATA.list_files(folder_name=config_vars["OUTPUT_FOLDER"], file_format="csv")
    file_count = len(files)

    print(f"NOTICE Checking in folder named '{config_vars['OUTPUT_FOLDER']}'")
    print(f"AVAILABLE FILES number {file_count}:")

    for idx, file_path in enumerate(files):
        buffer = str(file_path).rsplit("/")
        print(f"[{idx+1}] {buffer[-1]}")

    choice = AUXFN.get_user_input(display_text="Enter the file to open ([0] to cancel):", return_type="int")
    if choice == 0:
        return

    # Continue soling the no data issue
    choice_file_path = files[choice-1]
    print(f"You have chosen the following file path: {choice_file_path}")
    read_status, file_data = RWDATA.read_operation(file_path=choice_file_path, field_names=config_vars["FIELD_NAMES"])
    #print("DEBUG", "plotter read_status:", read_status, ", plotter file_data:", file_data)

    field_name_points = config_vars["FIELD_NAMES"][1]
    field_name_min_freq = config_vars["FIELD_NAMES"][2]
    field_name_min_mag = config_vars["FIELD_NAMES"][3]
    field_name_min_imp = config_vars["FIELD_NAMES"][4]
    field_name_trace_data = config_vars["FIELD_NAMES"][5]
    field_name_cutoff_mag = config_vars["FIELD_NAMES"][8]
    field_name_startf = config_vars["FIELD_NAMES"][11]
    field_name_stopf = config_vars["FIELD_NAMES"][12]
    extracted_data = [{"startf": row[field_name_startf], "stopf": row[field_name_stopf], "pts": row[field_name_points], "cutoff": row[field_name_cutoff_mag], "freq": row[field_name_min_freq], "mag": row[field_name_min_mag], "imp": row[field_name_min_imp], "trace": row[field_name_trace_data]} for row in file_data]
    extracted_data.pop(0)

    # print("DEBUG", f"minpt_list data: {minpt_list}")

    for idx, val in enumerate(extracted_data):
        plot_graph(data=val)


def plot_graph(data: dict):
    sweep_start_f = data["startf"]
    sweep_stop_f = data["stopf"]
    sweep_range = sweep_stop_f - sweep_start_f

    target_cutoff_mag = data["cutoff"]

    trace_point_count = data["pts"]
    trace_point_delta = sweep_range / (trace_point_count - 1)
    corresponding_trace_freq = [idx*trace_point_delta+sweep_start_f for idx in range(0, trace_point_count)]
    interpolated_trace = scipy.interpolate.interp1d(corresponding_trace_freq, data["trace"])

    # Generate a detailed trace using the interpolated trace function
    default_trace_points = 1000
    detail_factor = 1
    detailed_trace_points = int(default_trace_points * detail_factor)

    detailed_trace_freq = numpy.linspace(start=sweep_start_f, stop=sweep_stop_f, endpoint=True, num=detailed_trace_points)
    detailed_trace_mag = [interpolated_trace(x) for x in detailed_trace_freq]

    intersection_points = list(CALC.intersect(numpy.asarray(detailed_trace_freq), numpy.asarray(detailed_trace_mag),
                                         numpy.asarray(target_cutoff_mag)))

    # Continue with the actual plotting function here