import yaml
import subprocess

from datetime import datetime

def hours_from_time(time_str):
    try:
        # Parse the input time string into a datetime object
        input_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        
        # Get the current time as a datetime object
        current_time = datetime.now()
        
        # Calculate the time difference in hours
        time_difference = input_time - current_time
        
        # Extract the total number of hours from the time difference
        hours = time_difference.total_seconds() / 3600  # 3600 seconds in an hour
        
        return int(hours)
    except ValueError:
        # Handle invalid time format
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


def load_cfg():
    config_file = 'dump.yaml'
    with open(config_file, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        return config

def schedule_shall_run(hours_cnt, interval, schedule):
    if 'interval' in schedule:
        interval = schedule['interval']
    if hours_cnt%interval == 0:
        return True
    return False

def main():
    delete_old_snap()
    config = load_cfg()
    while space_limit_hit(config):
        delete_oldest_snap()
    time_str = config['start_time']
    hours_count = hours_from_time(config['start_time'])
    if hours_count is not None:
        interval = config['schedules']['interval']
        for vm in config['schedules']['vms']:
            print(f'vm={vm}')



main()
