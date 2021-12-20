#!/bin/env python
from subprocess import getstatusoutput
from pathlib import Path
import time
from datetime import datetime, date
import os
import json
import sys

# this is the location of pkgutil installation, ie: `where pkgutil`
PKGUTIL_LOCATION = "/usr/sbin/pkgutil"

def get_last_log_file(dir):
    '''Return the last modified .json file from a directory.'''
    log_dir = Path(dir)
    paths = log_dir.glob('*.json')
    try:
        return max(paths, key=os.path.getctime)
    except:
        return
    
def rmdir(directory):
    directory = Path(directory)
    try:
        for item in directory.iterdir():
            if item.is_dir():
                rmdir(item)
            else:
                item.unlink()
        directory.rmdir()
    except:
        pass


def datetime_to_string(value):
    '''Converts an date or datetime object to string. 
    This function can be supplied to json.dump() as a default attribute.'''
    if isinstance(value, datetime) or isinstance(value, date):
        return value.isoformat()
    else:
        raise TypeError(f"Object of type {type(value)} is not JSON serializable.")


def write_log(dir, filename, data):
    '''Give filename, data, write data to the logs directory, 
    with date and time appended to filename.'''
    log_dir = Path(dir)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    path = log_dir/filename
    filename_with_time = path.parent/f"{path.stem}-{timestr}{path.suffix}"
    Path(filename_with_time.parent).mkdir(parents=True, exist_ok=True)

    with open(filename_with_time.resolve(),  'w+') as f:
        if type(data) is str:
            f.write(data)
        else:
            json.dump(data, f, default=datetime_to_string)

    print(f"Saved to {filename_with_time.resolve()}")
    return filename_with_time


def get_prev_log_data():
    '''Return previous log data from file.'''
    last_log_file = get_last_log_file("logs/")
    if last_log_file is None:
        return

    with open(last_log_file.resolve(), 'r') as f:
        data = json.load(f)
    return data


def make_new_log():
    '''Creates new log, write to file, return log data.'''
    status, output = getstatusoutput(f"{PKGUTIL_LOCATION} --pkgs")
    if status == 0:
        packages = output.splitlines()
        write_log("logs", "installed.json", packages)
        return packages
    else:
        raise Exception("Command failed.")


def compare_log_packages(prev, curr):
    prev_set = set(prev) if prev else set()
    curr_set = set(curr) if curr else set()

    removed = sorted(list(prev_set.difference(curr_set)))
    installed = sorted(list(curr_set.difference(prev_set)))
    return removed, installed
    
def make_report(removed, installed):
    msg = ""
    msg += f" ####### Packages removed ####### \n"
    for i in removed:
        msg += i + "\n"
    msg += f" \n###### Packages installed ######\n"
    for i in installed:
        msg += i + "\n"
    return msg

def notify_mac(title, msg):
    os.system(f"""
              osascript -e 'display notification "{msg}" with title "{title}"'
              """)


if __name__ == "__main__":
    os.chdir(Path(__file__).parent.resolve())
    
    arguments = sys.argv[1:]
    if "--clear" in arguments:
        rmdir("logs")
        rmdir("reports")
        exit(0)
    
    prev_data = get_prev_log_data()
    curr_data = make_new_log()
    removed, installed = compare_log_packages(prev_data, curr_data)
    if removed or installed:
        report = make_report(removed, installed)
        notify_mac("pkg-watch detected changes!", f"Detected {len(installed)} new packages, {len(removed)} packages removed.")
        write_log("reports", "changes.txt", report)
        print(report)
    else:
        print("No change detected.")
    