import time
import yaml
import subprocess
import shlex
import json

# Function to read the execution counter from file
def read_counter(filename):
    try:
        with open(filename, 'r') as file:
            counter_data = json.load(file)
            return counter_data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tick_count": 0, "timestamp": 0}

# Function to write the execution counter to file
def write_counter(filename, counter_data):
    with open(filename, 'w') as file:
        json.dump(counter_data, file)


# Function to run a task command
def run_task_command(command, execution_count):
    command = command.replace("{cnt}", str(execution_count))
    subprocess.run(shlex.split(command), shell=True)

if __name__ == "__main__":
    counter_file = "execution_counter.json"

    # Read the previous execution counter data
    prev_counter_data = read_counter(counter_file)
    prev_tick_count = prev_counter_data["tick_count"]
    prev_timestamp = prev_counter_data["timestamp"]

    # Calculate the tick count since the last execution
    tick_count = prev_tick_count + 1

    # Calculate the elapsed time since the last execution
    current_time = time.time()
    elapsed_time = current_time - prev_timestamp
    print("Elapsed time since last run:", elapsed_time, "seconds")

    # Update the counter data
    counter_data = {"tick_count": tick_count, "timestamp": current_time}
    write_counter(counter_file, counter_data)


    # Read the task configuration from config.yaml
    try:
        with open("config.yaml", 'r') as config_file:
            config = yaml.safe_load(config_file)
            for task in config['tasks']:
                task_name = task['name']
                task_command = task['command']
                task_interval = task['interval']
                
                if elapsed_time >= task_interval:
                    run_task_command(task_command, prev_counter // task_interval)
    except FileNotFoundError:
        print("Config file 'config.yaml' not found.")
    except KeyError:
        print("Invalid or missing task configuration in config.yaml.")

