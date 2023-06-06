#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 2023

@author: elviskasonlin
"""
import operator

import scipy
import numpy

def intersect(x: np.array, f: np.array, g: np.array) -> Iterable[Tuple[(int, int)]]:
    """
    Finds the intersection points between `f` and `g` on the domain `x`.
    Given:
        - `x`: The discretised domain.
        - `f`: The discretised values of the first function calculated on the
               discretised domain.
        - `g`: The discretised values of the second function calculated on the
               discretised domain.
    Returns:
        An iterable containing the (x,y) points of intersection.
    """
    idx = np.argwhere(np.diff(np.sign(f - g))).flatten()
    return zip(x[idx], f[idx])


def get_trace_analysis(target_cutoff_mags: list, sweep_start_f: float, sweep_stop_f: float, trace_data: list):
    # Get interpolated trace
    sweep_range = sweep_stop_f - sweep_start_f

    trace_point_count = len(trace_data)
    trace_point_delta = sweep_range / (trace_point_count - 1)
    corresponding_trace_freq = [idx*trace_point_delta+sweep_start_f for idx in range(0, pts)]
    interpolated_trace = scipy.interpolate.interp1d(corresponding_trace_freq, trace_data)

    # Generate a detailed trace using the interpolated trace function
    default_trace_points = 1000
    detail_factor = 1
    detailed_trace_points = int(default_trace_points * detail_factor)

    detailed_trace_freq = numpy.linspace(start=sweep_start_f, stop=sweep_stop_f, endpoint=True, num=detailed_trace_points)
    detailed_trace_mag = [interpolated_trace(x) for x in detailed_trace_freq]

    # Find the minimum S11 point in the trace
    min_point = scipy.optimize.minimize_scalar(interpolated_trace, method="bounded", bounds=(sweep_start_f, sweep_stop_f))

    # Run through the target magnitudes, placing priority on the more negative numbers
    sorted_target_magnitudes = sorted(target_cutoff_mags, reverse=True)
    is_cutoff_successful = False
    cnt_max = len(sorted_target_magnitudes)
    cnt_cur = 0
    while is_cutoff_successful is False:
        if len(intersection_points) < 2:
            cnt_cur = cnt_cur + 1
            continue
        elif cnt_cur >= cnt_max:
            is_cutoff_successful = False
            break
        else:
            # Create a line of target mag measurement with the same number of points as the trace
            target_cutoff_func = [sorted_target_magnitudes[cnt_cur] for x in detailed_trace_freq]

            intersection_points = list(intersect(numpy.asarray(detailed_trace_freq), numpy.asarray(detailed_trace_mag),
                                                 numpy.asarray(target_cutoff_func)))

            # Get the distance of intersect points to the minimum point and save as a dictionary
            intersect_points_list_of_dicts = list()
            for pt in intersection_points:
                freq = pt[0]
                mag = pt[1]
                dist = abs(min_point["x"] - freq)
                entry_buffer = {"freq": freq, "mag": mag, "dist": dist}
                intersect_points_list_of_dicts.append(entry_buffer)

            # Sort the points by distance
            sorted_intersect_points = sorted(intersect_points_list_of_dicts, key=operator.itemgetter("dist"))

            # Get closest points
            closest_intersect_points = [sorted_intersect_points[0], sorted_intersect_points[1]]

            # Get bandwidth and Q factor
            bandwidth = abs(closest_intersect_points[0]["freq"] - closest_intersect_points[1]["freq"])
            q_factor = min_point["x"] / bandwidth
            print(
                f"For minimum point at {min_point['x']} with mag {min_point['fun']}, bandwidth: {bandwidth}, Q factor: {q_factor}")

    # Check for two closest intersection points from the center frequency at the set db target
    #   Search for the next best target if it's not found
    #   Iterate until two points are found
    # Calculate bandwidth between these two points
    # Calculate the Q factor using these two points


def process_trace_data():
    # Load trace data from csv file
    # For each entry, get the trace analysis results (Q factor and bandwidth)
    # Save the trace analysis results to the same csv file

    pass


def debug_plots(curve1x, curve1y, curve2x, curve2y):
    return