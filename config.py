import yaml

class ConfigManager:
    def __init__(self, config_file_path = 'config.yaml'):
        self.config_file_path = config_file_path
        self.config_data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file_path, 'r') as file:
                config_data = yaml.safe_load(file)
                return config_data or {}
        except FileNotFoundError:
            # If the file doesn't exist, return an empty dictionary
            return {}

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value

    def get_snap_interval(self, vmid):
        interval = self.config_data['schedules']['interval']
        vms = self.config_data['schedules']['vms']
        for vm in vms:
            if vm['vmid'] == int(vmid):
                interval = vm['interval']
                break
        print(f'get-snap-interval: {vmid} = {interval}')
        return interval

    def set_snap_interval(self, vmid, interval):
        if interval != self.get_snap_interval(vmid):
            cint = self.config_data['schedules']['interval']
            vms = self.config_data['schedules']['vms']
            for vm in vms:
                if vm['vmid'] == int(vmid):
                    if cint == interval:
                        vms.remove(vm)
                    else:
                        vm['interval'] = interval
                    self.save_config()
                    break

    def save_config(self):
        with open(self.config_file_path, 'w') as file:
            yaml.dump(self.config_data, file)

