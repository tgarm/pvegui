import subprocess
import sys


class Snapshot:
    def __init__(self, vmid):
        self.vmid = vmid
        self.states = self.capture_vm_states(vmid)
        self.vmsize = int(self.calculate_total_vm_size(self.states))

# Function to capture and format the output
    def capture_vm_states(self,vmid):
        # Run lsblk and capture its output
        lsblk_output = subprocess.check_output(["lsblk"], universal_newlines=True)

        # Initialize variables to track state and capture text
        state = 0
        vm_states = []

        # Split the lsblk output into lines
        lines = lsblk_output.splitlines()

        # Iterate through each line
        for line in lines:
            # Trim leading and trailing whitespace
            line = line.strip()

            # Check if the line contains '└─pve-data_tdata' and state is 0
            if '└─pve-data_tdata' in line and state == 0:
                # Set state to 1 (0 -> 1)
                state = 1

            # Check if the line contains '└─pve-data-tpool' and state is 1
            elif state == 1 and '└─pve-data-tpool' in line:
                # Set state to 2 (1 -> 2)
                state = 2

            # Check if the line starts with '└─' and the state is 2
            elif state == 2:
                if line.startswith('└─'):
                    state = 3

                # If the line contains 'pve-vm--{vmid}--state--', capture the text after it
                if f'pve-vm--{vmid}--state--' in line:
                    capture_text = line.split(f'pve-vm--{vmid}--state--', 1)[-1].strip()
                    # Split capture_text by whitespace and extract VM name and size
                    fields = capture_text.split()
                    if len(fields) >= 4:
                        vm_name = fields[0]
                        vm_size = fields[3]
                        vm_states.append([vm_name, vm_size])

            # Print the captured text when the state is 3
            if state == 3:
                break

        return vm_states

    def calculate_total_vm_size(self,vm_states):
        total_size_bytes = 0
        size_units = {'G': 1e9, 'M': 1e6, 'K': 1e3, 'T': 1e12}

        for vm_name, vm_size in vm_states:
            # Extract the size value and unit
            size_value, size_unit = float(vm_size[:-1]), vm_size[-1]

            # Convert the size to bytes based on the unit
            if size_unit in size_units:
                total_size_bytes += size_value * size_units[size_unit]

        return total_size_bytes
if __name__ == "__main__":
# Check if a VMID argument is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <VMID>")
        sys.exit(1)

# Extract the VMID from the command-line argument
    vmid = sys.argv[1]
    snap = Snapshot(vmid)

    for item in snap.states:
        print(item)
    print(f'Total size: {snap.vmsize} bytes')

