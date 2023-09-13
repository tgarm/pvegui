import yaml

data = {
    'limits': {
        'space_usage_threshold': 70
        },
    'schedules':{
        'interval': 24,
        'vms':[
        {   'vmid': 201, 'interval': 8 },
        {   'vmid': 202, 'interval': 4 }
        ]
    }
}

with open("dump.yaml", 'w') as file:
    yaml.dump(data, file)
