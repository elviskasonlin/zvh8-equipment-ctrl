#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 2023

@author: elviskasonlin
"""

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

def get_trace_analysis(target_cutoff_mag: float, sweep_start_f: float, sweep_stop_f: float, trace_data: list):
    sweep_range = sweep_stop_f - sweep_start_f

    trace_point_count = len(trace_data)
    trace_point_delta = sweep_range / (trace_point_count - 1)
    corresponding_trace_freq = [idx*trace_point_delta+sweep_start_f for idx in range(0, pts)]
    interpolated_trace = scipy.interpolate.interp1d(corresponding_trace_freq, trace_data)

    default_trace_points = 1000
    detail_factor = 1
    detailed_trace_points = int(default_trace_points * detail_factor)

    detailed_trace_freq = numpy.linspace(start=sweep_start_f, stop=sweep_stop_f, endpoint=True, num=detailed_trace_points)
    detailed_trace_mag = [interpolated_trace(x) for x in detailed_trace_freq]

    min_point = scipy.optimize.minimize_scalar(interpolated_trace, method="bounded", bounds=(sweep_start_f, sweep_stop_f))

    target_cutoff_func = [target_cutoff_mag for x in detailed_trace_freq]

    intersection_points = list(intersect(numpy.asarray(detailed_trace_freq), numpy.asarray(detailed_trace_mag), numpy.asarray(target_cutoff_func)))

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