#!/usr/bin/env python3

import os
import yaml
import subprocess

import libpve

from datetime import datetime

pve = libpve.LibPVE()

def load_yaml_config(yaml_filename, app_name):
    # Initialize search directories
    search_directories = [
        os.path.expanduser("~"),
        os.path.join(os.path.expanduser("~"), '.config'),
        os.path.join(os.path.expanduser("~"), '.config', app_name),
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__))
    ]

    for directory in search_directories:
        file_path = os.path.join(directory, yaml_filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as yaml_file:
                try:
                    config = yaml.safe_load(yaml_file)
                    return config
                except yaml.YAMLError as e:
                    raise ValueError(f"Error parsing YAML file '{yaml_filename}' in {directory}: {e}")

    raise FileNotFoundError(f"YAML file '{yaml_filename}' not found in the expected locations.")


def hours_from_time(time_str):
    try:
        input_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        time_difference = current_time - input_time 
        hours = time_difference.total_seconds() / 3600  # 3600 seconds in an hour
        return int(hours)
    except ValueError:
        return None

def space_limit_hit(config):
    threshold = config['limits']['space_threshold']

    lvdisplay_output = subprocess.check_output(['sudo', 'lvdisplay', '-C', '/dev/pve/data'], universal_newlines=True)

    lines = lvdisplay_output.split('\n')
    for line in lines:
        if 'data' in line:
            data_percent = float(line.split()[4])
            break

    print(f"Volume space usage: {data_percent}%")
    return data_percent > threshold

def delete_old_snap():
    lines = subprocess.check_output("sudo lvdisplay -C|grep  -i 'sched-'|awk '{print $1}'", shell=True, universal_newlines=True).split('\n')
    vmids = {}
    old_snap = 0
    for line in lines:
        fields = line.split('-')
        if len(fields)>1:
            snap_id = int(fields[-1])
            if not snap_id in vmids:
                vmids[snap_id] = {}
            vmids[snap_id][fields[1]] = line
            if old_snap==0 or old_snap > snap_id:
                old_snap = snap_id
    if old_snap!=0:
        print(f'delete old snap: {old_snap}')
        for vmid in vmids[old_snap].keys():
            name = vmids[old_snap][vmid]
            print(f'sudo qm delsnapshot {vmid} {name}')

def newest_snap_idx(vmid):
    lines = subprocess.check_output("sudo lvdisplay -C|grep  -i 'sched-'|awk '{print $1}'", shell=True, universal_newlines=True).split('\n')
    idx = 0
    for line in lines:
        fields = line.split('-')
        if len(fields)>1:
            snap_id = int(fields[-1])
            if vmid == fields[1]:
                if idx < snap_id:
                    idx = snap_id
    return idx

def schedule_shall_run(hours_cnt, interval, schedule):
    if 'interval' in schedule:
        interval = schedule['interval']
    if hours_cnt%interval == 0:
        return True
    return False

def make_snapshot(vmid, idx):
    pve.snapshot(vmid, f'sched-{idx}', f'auto snapshot for {vmid}', reload=False)

def main():
    config = load_yaml_config('dump.yaml', 'pvegui')
    while space_limit_hit(config):
        delete_oldest_snap()
    time_str = config['start_time']
    hours_count = hours_from_time(config['start_time'])
    if hours_count is not None:
        interval = config['schedules']['interval']
        for vm in config['schedules']['vms']:
            vmid = vm['vmid']
            exact = hours_count % vm['interval']
            if exact == 0:
                idx = newest_snap_idx(vmid)
                print(f'vm: {vmid} hours: {hours_count}, idx: {idx}')
                if idx < hours_count:
                    make_snapshot(vm['vmid'], hours_count)

main()
