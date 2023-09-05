#!/bin/bash

# Check if the script argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <python_script>"
    exit 1
fi

# Get the directory of the script
script_dir="$(dirname "$1")"

# Activate virtual environment if 'venv' exists in the script's directory
venv_path="$script_dir/venv"
if [ -d "$venv_path" ]; then
    source "$venv_path/bin/activate"
fi

# Execute the Python script
python3 "$1"

# Deactivate the virtual environment
deactivate 2>/dev/null

