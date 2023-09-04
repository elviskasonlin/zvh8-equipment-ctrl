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


def read_operation(file_path: pathlib.PosixPath, field_names: list):
    return_data, status = list(), bool()
    with open_f(file=file_path, newline="", mode="r") as (csvfile, err):
        if err:
            print("IOError when reading the file!", err)
            status = False
        else:
            # Continue solving the no data issue
            #print(f"DEBUG csvfile: {csvfile}, field_names: {field_names}")
            reader = csv.DictReader(csvfile, field_names)
            #print("DEBUG", reader)
            for row in reader:
                #print("DEBUG", type(row), row)
                return_data.append(row)
            status = True
        return status, return_data


def list_files(folder_name: str, file_format: str):
    dir_location = pathlib.Path.cwd().joinpath(f"{folder_name}/")
    file_path_list = dir_location.glob(f"*.{file_format}")
    files = [x for x in file_path_list if x.is_file()]
    return files


def make_dir(folder_path: pathlib.Path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        return None
    return
