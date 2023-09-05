#!/bin/bash

# Specify the command to be invoked by sudo user
SDCMD="/usr/sbin/qm"

# Specify the file to be modified by sudo user
NETCFG_PATH="path_to_your_file"

# Specify the backup file path for the modified file
NETCFG_BAK="path_to_backup_file"

# Ensure three arguments are provided: old file path, new file name, and new file backup name
if [ $# -ne 3 ]; then
    echo "Usage: $0 <old_file_path> <new_file_name> <new_file_backup_name>"
    exit 1
fi

old_file_path="$1"
new_file_name="$2"
new_file_backup_name="$3"

# Check if the old file exists
if [ ! -f "$old_file_path" ]; then
    echo "File '$old_file_path' does not exist."
    exit 1
fi

# Extract the directory path from the old file path
directory_path=$(dirname "$old_file_path")

# Construct the new file path with the updated file name
new_file_path="$directory_path/$new_file_name"

# Rename the file by moving it to the new file path with force
mv -f "$old_file_path" "$new_file_path"

# Check if the renaming was successful
if [ $? -eq 0 ]; then
    echo "File renamed from '$old_file_path' to '$new_file_path'."
else
    echo "Failed to rename the file."
    exit 1
fi

# Add sudo configuration for the specified command
echo "%sudo ALL=(ALL:ALL) NOPASSWD: $SDCMD" >> /etc/sudoers

# Check if sudo configuration was successfully added
if [ $? -eq 0 ]; then
    echo "Sudo configuration for '$SDCMD' added successfully."
else
    echo "Failed to add sudo configuration."
fi

# Change permissions of the modified file to allow editing by sudo users
sudo chown :sudo "$NETCFG_PATH"
sudo chmod g+w "$NETCFG_PATH"

# Create a backup of the modified file
sudo cp "$NETCFG_PATH" "$NETCFG_BAK"

# Check if the backup was successful
if [ $? -eq 0 ]; then
    echo "Backup of '$NETCFG_PATH' created as '$NETCFG_BAK'."
else
    echo "Failed to create a backup of '$NETCFG_PATH'."
fi

