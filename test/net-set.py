#!/usr/bin/env python3

import os
import sys

def create_interface_config(interface_name):
    #interfaces_dir = "/etc/network/interfaces.d"
    interfaces_dir = "interfaces.d"
    interface_config_path = os.path.join(interfaces_dir, f"{interface_name}.conf")

    if os.path.exists(interface_config_path):
        print(f"Configuration file for '{interface_name}' already exists.")
        return

    config_content = f"auto {interface_name}\niface {interface_name} inet dhcp\n"

    try:
        with open(interface_config_path, "w") as config_file:
            config_file.write(config_content)
        print(f"Configuration file for '{interface_name}' created at '{interface_config_path}'.")
    except Exception as e:
        print(f"Failed to create the configuration file for '{interface_name}': {e}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <remove_old_config>")
        sys.exit(1)

    remove_old_config = sys.argv[1].lower() == "true"
    interfaces_path = "/etc/network/interfaces"
    auto_interfaces = []

    try:
        with open(interfaces_path, "r") as interfaces_file:
            for line in interfaces_file:
                if line.strip().startswith("auto") and "lo" not in line:
                    auto_interfaces.extend(line.strip().split()[1:])
    except Exception as e:
        print(f"Error reading '{interfaces_path}': {e}")
        sys.exit(1)

    for interface_name in auto_interfaces:
        create_interface_config(interface_name)

    if remove_old_config:
        try:
            with open(interfaces_path, "r") as old_interfaces_file:
                old_lines = old_interfaces_file.readlines()

            with open(interfaces_path, "w") as new_interfaces_file:
                for line in old_lines:
                    if "auto" in line and any(interface_name in line for interface_name in auto_interfaces):
                        continue
                    new_interfaces_file.write(line)
            print("Old interface configurations removed from '/etc/network/interfaces'.")
        except Exception as e:
            print(f"Error removing old configurations: {e}")

if __name__ == "__main__":
    main()

