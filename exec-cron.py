import os
import sys
import shutil
import yaml
import re

def parse_disk_space(value):
    value = value.strip().upper()
    match = re.match(r'^(\d+)\s*(B|KB|MB|GB|TB)?$', value)
    if match:
        size = int(match.group(1))
        unit = match.group(2) or 'B'
        units = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
        return size * units[unit]
    else:
        raise ValueError(f"Invalid disk space value: {value}")

def get_directory_size(directory):
    if not directory or not os.path.exists(directory):
        return 0

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def delete_oldest_file(directory):
    files = [(f, os.path.getmtime(os.path.join(directory, f))) for f in os.listdir(directory)]
    oldest_file = min(files, key=lambda x: x[1])[0]
    os.remove(os.path.join(directory, oldest_file))
    print(f"Deleted oldest file: {oldest_file}")

def execute_task(command):
    os.system(command)

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <task_name>")
        return

    task_name = sys.argv[1]
    config_file = "config.yaml"

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    if task_name == "list":
        print("Available tasks:")
        for task in config["tasks"]:
            print(task["name"])
        return

    selected_task = None
    for task in config["tasks"]:
        if task["name"] == task_name:
            selected_task = task
            break

    if selected_task is None:
        print(f"Task '{task_name}' not found.")
        return

    task_dir = selected_task["directory"]
    max_disk_space = parse_disk_space(selected_task["max_disk_space"])
    task_command = selected_task["command"]

    current_directory_size = get_directory_size(task_dir)

    if current_directory_size > max_disk_space:
        while current_directory_size > max_disk_space:
            delete_oldest_file(task_dir)
            current_directory_size = get_directory_size(task_dir)
        print("Sufficient disk space available after cleanup.")
    else:
        print("Sufficient disk space available.")

    execute_task(task_command)


if __name__ == "__main__":
    main()

