#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 2023

@author: elviskasonlin
"""

import matplotlib
import src.rw_data as RWDATA
import src.aux_fns as AUXFN
import pandas as pd

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
    print("DEBUG", "plotter read_status:", read_status, ", plotter file_data:", file_data)
    field_name = config_vars["FIELD_NAMES"][5]
    trace_data = [row[field_name] for row in file_data]
    trace_data.pop(0)
    print("DEBUG", f"trace_data len: {len(trace_data)}, trace_data type: {type(trace_data)}, trace_data data: {trace_data}")

    # Debugging and visualisation
    df = pd.DataFrame(file_data)
    print(df)

    #plot_graph()

def plot_graph():
    pass


# The following function below is adapted from the logic used in the file
# `calculate.py` for use in getting trace analysis data (Q Factor, BW, etc.)
# def get_trace_analysis(target_cutoff_mags: list, sweep_start_f: float, sweep_stop_f: float, trace_data: list):
#     """
#     Provided a list of target cutoff magnitudes, sweep range, and trace, it will process and calculate the bandwidth and q factor.
#     Args:
#         target_cutoff_mags: A list of target magnitudes to calculate bandwidth. Typically -10, -6, and -3
#         sweep_start_f: Starting frequency in MHz
#         sweep_stop_f: Stop frequency in MHz
#         trace_data: The trace data as a list
#
#     Returns:
#         A dictionary object addressable with {is_successful, bandwidth, q_factor, cutoff_mag}
#     """
#     # Get interpolated trace
#     sweep_range = sweep_stop_f - sweep_start_f
#
#     trace_point_count = len(trace_data)
#     trace_point_delta = sweep_range / (trace_point_count - 1)
#     corresponding_trace_freq = [idx*trace_point_delta+sweep_start_f for idx in range(0, trace_point_count)]
#     interpolated_trace = scipy.interpolate.interp1d(corresponding_trace_freq, trace_data)
#
#     # Generate a detailed trace using the interpolated trace function
#     default_trace_points = 1000
#     detail_factor = 1
#     detailed_trace_points = int(default_trace_points * detail_factor)
#
#     detailed_trace_freq = numpy.linspace(start=sweep_start_f, stop=sweep_stop_f, endpoint=True, num=detailed_trace_points)
#     detailed_trace_mag = [interpolated_trace(x) for x in detailed_trace_freq]
#
#     # Find the minimum S11 point in the trace
#     min_point = scipy.optimize.minimize_scalar(interpolated_trace, method="bounded", bounds=(sweep_start_f, sweep_stop_f))
#
#     # Run through the target magnitudes, placing priority on the more negative numbers
#     sorted_target_magnitudes = sorted(target_cutoff_mags, reverse=True)
#     # Sorted in ascending order
#     is_cutoff_successful = False
#     cnt_max = len(sorted_target_magnitudes)
#     cnt_cur = 0
#
#     # Return variable initialisation
#     bandwidth, q_factor, final_cutoff_mag = None, None, None
#
#     while is_cutoff_successful is False:
#         if cnt_cur >= cnt_max:
#             print("Exceeded count max. Breaking...")
#             break
#
#         # Create a line of target mag measurement with the same number of points as the trace
#         target_cutoff_func = [sorted_target_magnitudes[cnt_cur] for x in detailed_trace_freq]
#         intersection_points = list(intersect(numpy.asarray(detailed_trace_freq), numpy.asarray(detailed_trace_mag),
#                                              numpy.asarray(target_cutoff_func)))
#
#         if len(intersection_points) < 2:
#             cnt_cur = cnt_cur + 1
#             continue
#         else:
#             # Get the distance of intersect points to the minimum point and save as a dictionary
#             intersect_points_list_of_dicts = list()
#             for pt in intersection_points:
#                 freq = pt[0]
#                 mag = pt[1]
#                 dist = abs(min_point["x"] - freq)
#                 entry_buffer = {"freq": freq, "mag": mag, "dist": dist}
#                 intersect_points_list_of_dicts.append(entry_buffer)
#
#             # Sort the points by distance
#             sorted_intersect_points = sorted(intersect_points_list_of_dicts, key=operator.itemgetter("dist"))
#
#             # Get closest points
#             closest_intersect_points = [sorted_intersect_points[0], sorted_intersect_points[1]]
#
#             # Check whether the two points are left and right of the minimum point
#             sorted_intersect_points_by_f = sorted(closest_intersect_points, key=operator.itemgetter("freq"))
#             if not ((sorted_intersect_points_by_f[0]["freq"] < min_point["x"]) and (min_point["x"] < sorted_intersect_points_by_f[1]["freq"])):
#                 cnt_cur = cnt_cur + 1
#                 continue
#
#             # Get bandwidth and Q factor
#             bandwidth = abs(closest_intersect_points[0]["freq"] - closest_intersect_points[1]["freq"])
#             q_factor = min_point["x"] / bandwidth
#             print(f"For minimum point at {min_point['x']} with mag {min_point['fun']}, bandwidth: {bandwidth}, Q factor: {q_factor}")
#             final_cutoff_mag = sorted_target_magnitudes[cnt_cur]
#             is_cutoff_successful = True