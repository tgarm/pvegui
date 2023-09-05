import os
import subprocess
from crontab import CronTab

# Specify the script name here
SCRIPT_NAME = 'make-snapshot'
PYLOADER = 'pyloader.sh'  

def get_current_username():
    return os.getlogin()

def get_script_real_path(script_name):
    # Check current directory
    if os.path.exists(script_name):
        return os.path.abspath(script_name)

    try:
        result = subprocess.run(['which', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        real_path = result.stdout.strip()
        return real_path
    except subprocess.CalledProcessError:
        print(f"Error: {script_name} not found.")
        return None

def get_make_snapshot_frequency(username):
    cron = CronTab(user=username)
    
    for job in cron:
        if SCRIPT_NAME in job.command:
            return job

def print_make_snapshot_frequency(username):
    job = get_make_snapshot_frequency(username)
    if job:
        print(f"Current {SCRIPT_NAME} frequency:", job)
    else:
        print(f"{SCRIPT_NAME} not found in crontab")

def set_make_snapshot_frequency(username, minute, hour, day):
    cron = CronTab(user=username)
    
    cron.remove_all(comment=SCRIPT_NAME)

    real_path = get_script_real_path(SCRIPT_NAME)
    if real_path:
        job = cron.new(command=f'{PYLOADER}/run_python_script.sh {real_path}', comment=SCRIPT_NAME)
        job.setall(f"{minute} {hour} {day} * *")
        cron.write()

if __name__ == "__main__":
    username = get_current_username()

    print_make_snapshot_frequency(username)

    # Set the script to run every 10 minutes
    set_make_snapshot_frequency(username, "*/10", "*", "*")
    print_make_snapshot_frequency(username)

