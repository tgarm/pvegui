def parse_resolv_conf(file_path):
    resolv_dict = {'nameserver':[]}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 2:
                key = parts[0].lower()
                value = ' '.join(parts[1:])
                if key in resolv_dict:
                    if isinstance(resolv_dict[key], list):
                        resolv_dict[key].append(value)
                    else:
                        resolv_dict[key] = [resolv_dict[key], value]
                else:
                    resolv_dict[key] = value
    if resolv_dict['nameserver']==None:
        resolv_dict['nameserver'] = []
    while len(resolv_dict['nameserver'])<3:
        resolv_dict['nameserver'].append('')
    return resolv_dict

def dict_to_resolv_conf(resolv_dict):
    resolv_conf = ""
    for key, value in resolv_dict.items():
        if isinstance(value, list):
            for v in value:
                resolv_conf += f"{key} {v}\n"
        else:
            resolv_conf += f"{key} {value}\n"
    return resolv_conf

def write_resolv_conf(resolv_dict, file_path='/etc/resolv.conf'):
    resolv_conf = ""
    for key, value in resolv_dict.items():
        if isinstance(value, list):
            # Remove empty items from the 'nameserver' list
            value = [v for v in value if v]
            for v in value:
                resolv_conf += f"{key} {v}\n"
        else:
            resolv_conf += f"{key} {value}\n"

    with open(file_path, 'w') as file:
        file.write(resolv_conf)



if __name__ == "__main__":
# Example usage:
    resolv_conf_file = '/etc/resolv.conf'
    resolv_dict = parse_resolv_conf(resolv_conf_file)
    print(resolv_dict)
    resolv_conf_body = dict_to_resolv_conf(resolv_dict)
    print(resolv_conf_body)
