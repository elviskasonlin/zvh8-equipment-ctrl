#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 2023

@author: elviskasonlin
"""

import src.rw_data as RWDATA
import src.aux_fns as AUXFN
import src.calculate as CALC
import operator
import numpy
import scipy
import matplotlib.pyplot as plt
from ast import literal_eval


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

    extracted_data = list()
    for idx, row in enumerate(file_data):
        if idx != 0:
            write_buffer_dict = {"startf": literal_eval(row[field_name_startf]),
                                 "stopf": literal_eval(row[field_name_stopf]),
                                 "pts": literal_eval(row[field_name_points]),
                                 "cutoff": literal_eval(row[field_name_cutoff_mag]),
                                 "mfreq": literal_eval(row[field_name_min_freq]),
                                 "mmag": literal_eval(row[field_name_min_mag]),
                                 "mimp": row[field_name_min_imp],
                                 "trace": literal_eval(row[field_name_trace_data])}
            extracted_data.append(write_buffer_dict)

    # print("DEBUG", f"minpt_list data: {minpt_list}")

    for idx, val in enumerate(extracted_data):
        plot_graph(data=val)


def plot_graph(data: dict):

    sweep_start_f = data["startf"]
    sweep_stop_f = data["stopf"]
    sweep_range = sweep_stop_f - sweep_start_f

    target_cutoff_mag = data["cutoff"]
    trace_point_count = len(data["trace"])
    trace_point_delta = sweep_range / (trace_point_count - 1)

    # Logic for whether to use a detailed trace
    detail_minimum_threshold = 1000
    detail_factor = 3
    detailed_trace_point_count = trace_point_count
    if trace_point_count < detail_minimum_threshold:
        detailed_trace_point_count = int(trace_point_count * detail_factor)

    # Setting up settings for trace
    corresponding_trace_freq = [idx*trace_point_delta+sweep_start_f for idx in range(0, trace_point_count)]
    cutoff_mag_trace = [target_cutoff_mag for idx in range(0, detailed_trace_point_count)]

    # Create an interpolated trace using scipy interpolate
    interpolated_trace = scipy.interpolate.interp1d(corresponding_trace_freq, data["trace"])

    # Generate a detailed trace using the interpolated trace function
    detailed_trace_freq = numpy.linspace(start=sweep_start_f, stop=sweep_stop_f, endpoint=True, num=detailed_trace_point_count)
    detailed_trace_mag = [interpolated_trace(x) for x in detailed_trace_freq]

    # Check for intersection points
    intersection_points = list(CALC.intersect(x=numpy.asarray(detailed_trace_freq), f=numpy.asarray(detailed_trace_mag),
                                              g=numpy.asarray(cutoff_mag_trace)))

    # Get the nearest intersection points

    # Get the distance of intersect points to the minimum point and save as a dictionary
    intersect_points_list_of_dicts = list()
    for pt in intersection_points:
        freq = pt[0]
        mag = pt[1]
        dist = abs(interpolated_trace(data["mfreq"]) - freq)
        entry_buffer = {"freq": freq, "mag": mag, "dist": dist}
        intersect_points_list_of_dicts.append(entry_buffer)

    # Sort the points by distance
    sorted_intersect_points = sorted(intersect_points_list_of_dicts, key=operator.itemgetter("dist"))

    # Get closest points
    closest_intersect_points = [sorted_intersect_points[0], sorted_intersect_points[1]]

    # Check whether the two points are left and right of the minimum point
    sorted_closest_intersect_points_by_f = sorted(closest_intersect_points, key=operator.itemgetter("freq"))
    is_error_intersect_pts_finder = False
    if not ((sorted_closest_intersect_points_by_f[0]["freq"] < data["mfreq"]) and (
            data["mfreq"] < sorted_closest_intersect_points_by_f[1]["freq"])):
        print("ERROR Issue with logic for checking whether intersect points left/right of minimum point in plotter.py")
        is_error_intersect_pts_finder = True

    print("DEBUG Intersection Points:", sorted_closest_intersect_points_by_f)
    print("DEBUG Point count:", len(detailed_trace_mag), len(detailed_trace_freq))

    # Continue with the actual plotting function here
    plt.plot(detailed_trace_freq, detailed_trace_mag, label='Interpolated', color="m", alpha=0.5)
    plt.plot(detailed_trace_freq, cutoff_mag_trace, label='Cut-off', color="g", alpha=0.5)
    plt.plot(data["mfreq"], interpolated_trace(data["mfreq"]), marker="x")
    print("Error?", is_error_intersect_pts_finder)
    if not is_error_intersect_pts_finder:
        plt.plot(sorted_closest_intersect_points_by_f[0]["freq"], sorted_closest_intersect_points_by_f[0]["mag"], marker="x", color="r")
        plt.plot(sorted_closest_intersect_points_by_f[1]["freq"], sorted_closest_intersect_points_by_f[1]["mag"], marker="x", color="r")
    plt.legend()
    plt.show()