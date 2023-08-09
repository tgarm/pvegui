import re
from shell import shell

class LibPVE():
    def __init__(self):
        self.vms = []

    def list(self):
        ls = shell('sudo qm list').output()
        if len(ls)>0:
            header = ls.pop(0)
            print(f'header=[{header}]')
            vms = []
            for line in ls:
                items = re.split('\s+', line.strip())
                if len(items)==6:
                    vms.append({
                        'id': items[0],
                        'name': items[1],
                        'status': items[2],
                        'ram': int(items[3]),
                        'bootdisk_gb': int(float(items[4])),
                        'pid': int(items[5])
                        })
                    print(f'line=[{vms}]')
            self.vms = vms
        return vms
    
    def start_vm(self, id):
        res = shell(f'sudo qm start {id}').output()
    def stop_vm(self, id):
        res = shell(f'sudo qm stop {id}').output()


