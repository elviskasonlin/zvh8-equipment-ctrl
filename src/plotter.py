#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 2023

@author: elviskasonlin
"""

import matplotlib
import src.rw_data as RWDATA
import src.aux_fns as AUXFN

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
    print(read_status, file_data)
    field_name = config_vars["FIELD_NAMES"][5]
    trace_data = [row[field_name] for row in file_data]
    print(trace_data)
    #plot_graph()

def plot_graph():

    pass
