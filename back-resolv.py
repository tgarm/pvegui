def dict_to_resolv_conf(resolv_dict):
    resolv_conf = ""
    for key, value in resolv_dict.items():
        if isinstance(value, list):
            for v in value:
                resolv_conf += f"{key} {v}\n"
        else:
            resolv_conf += f"{key} {value}\n"
    return resolv_conf

# Example usage:
resolv_dict = {
    'search': 'domain-0xx.local',
    'nameserver': ['8.8.8.8', '223.5.5.5']
}

resolv_conf_body = dict_to_resolv_conf(resolv_dict)
print(resolv_conf_body)
