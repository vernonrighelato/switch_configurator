def add_vlan(vlan_id, vlan_name, port_channel_ids):
    config_strings = []
    config_strings.append('en\nblackhawks\nconf t\n')
    config_strings.append(f"vlan {vlan_id}\nname {vlan_name}\nexit")
    for id in port_channel_ids:
        config_strings.append(f"interface Po{id}")
        config_strings.append(f"switchport trunk allowed vlan add {vlan_id}\nexit")
    config_strings.append("end\nwri\nexit\n")
    return "\n".join(config_strings)

print(add_vlan(346, "TOTP", ['51', '52']))

