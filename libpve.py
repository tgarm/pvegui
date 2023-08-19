import re
from datetime import datetime
from shell import shell

class LibPVE():
    def __init__(self):
        self.vms = []
        self.snaps = {}

    def list(self):
        ls = shell('sudo qm list').output()
        if len(ls)>0:
            header = ls.pop(0)
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
            self.vms = vms
        return vms

    def start_vm(self, id):
        res = shell(f'sudo qm start {id}').output()
    def stop_vm(self, id):
        res = shell(f'sudo qm stop {id}').output()

    def list_snapshots(self, id):
        res = shell(f'sudo qm listsnapshot {id}').output()
        self.snaps[id] = []
        for line in res:
            items = re.split('\s+', line.strip(), maxsplit=4)
            if len(items)==5 and len(items[2])==10:
                self.snaps[id].append({
                    'name': items[1],
                    'desc': items[4],
                    'time': datetime.strptime(f'{items[2]} {items[3]}', '%Y-%m-%d %H:%M:%S')
                    })
            elif len(items)==5 and items[1]=='current':
                continue
            else:
                print(f'unknown snapshot item: {items}')

    def snapshot(self, id, name, desc='nothing'):
        res = shell(f'sudo qm snapshot {id} "{name}" -description "{desc}"').output()
        self.list_snapshots(id)
        return res



