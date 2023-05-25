#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 2023

@author: elviskasonlin
"""
import datetime
import os
import pathlib
import csv
import contextlib

@contextlib.contextmanager
def open_f(file, newline, mode):
    try:
        f = open(file=file, newline=newline, mode=mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()
def initialise_results_file(config_vars: dict, field_names: list, timestamp: str):
    folder_name = config_vars["OUTPUT_FOLDER"]
    file_name = config_vars["OUTPUT_FILE_NAME"]

    dir_location = pathlib.Path.cwd().joinpath(f"{folder_name}/")
    print("DEBUG dir_location", dir_location)
    if not os.path.exists(dir_location):
        os.makedirs(dir_location, exist_ok=False)

    if timestamp != "":
        file_path = dir_location.joinpath(file_name + "-" + timestamp + ".csv")
    else:
        file_path = dir_location.joinpath(file_name + ".csv")

    print("DEBUG file_path", file_path)
    with open_f(file=file_path, newline="", mode="w") as (csvfile, err):
        if err:
            print("IOError when initialising the results file!", err)
            return False
        else:
            writer = csv.DictWriter(csvfile, field_names)
            writer.writeheader()
    return True

def write_operation(config_vars: dict, data: list, field_names: list, timestamp: str):
    folder_name = config_vars["OUTPUT_FOLDER"]
    file_name = config_vars["OUTPUT_FILE_NAME"]
    dir_location = pathlib.Path.cwd().joinpath(f"{folder_name}/")
    file_path = None
    if timestamp != "":
        file_path = dir_location.joinpath(file_name + "-" + timestamp + ".csv")
    else:
        file_path = dir_location.joinpath(file_name + ".csv")

    with open_f(file=file_path, newline="", mode="a+") as (csvfile, err):
        if err:
            print("IOError when initialising the results file!", err)
            return False
        else:
            writer = csv.DictWriter(csvfile, field_names)
            writer.writerows(data)
    return True