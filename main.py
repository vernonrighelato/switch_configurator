import os
from dotenv import load_dotenv
import paramiko
from netmiko import ConnectHandler
from data_utils import *
from file_utils import load_hosts, write_tuple
from config_utils import add_vlan

load_dotenv()
#Edits made in dev branch
JUMP_HOST = "netgate.ddns.eng.ox.ac.uk"
JUMP_USER = os.environ["JUMP_USER"]
JUMP_PASS = os.environ["JUMP_PASS"]
TARGET_USER = os.environ["TARGET_USER"]
TARGET_PASS = os.environ["TARGET_PASS"]
TARGET_PORT = 22
ENABLE_SECRET = os.environ["ENABLE_SECRET"]

def create_jump_client():
    jump_client = paramiko.SSHClient()
    jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to netgate")
    jump_client.connect(
        hostname=JUMP_HOST,
        username=JUMP_USER,
        password=JUMP_PASS,
        look_for_keys=False,
        allow_agent=False
    )
    return jump_client

def create_tunnel(jump_client, TARGET_HOST):
    transport = jump_client.get_transport()   
    chan = transport.open_channel(
        kind="direct-tcpip",
        dest_addr=(TARGET_HOST, TARGET_PORT),
        src_addr=("127.0.0.1", 0)
    )
    return chan

def connect_to_target_via_tunnel(jump_client, TARGET_HOST, command_set):
    # command_set = load_command_set('show_ints.txt')
    output_strings = []
    chan = None
    net_conn = None
    try:
        chan = create_tunnel(jump_client, TARGET_HOST)
        device = {
            "device_type": "cisco_ios",
            "host": TARGET_HOST,
            "username": TARGET_USER,
            "password": TARGET_PASS,
            "secret": ENABLE_SECRET,
            "sock": chan,
        }
        print(f"Connecting to {TARGET_HOST} via netgate")
        net_conn = ConnectHandler(**device)
        print(f"sending commands {command_set}")
        net_conn.enable() # Enable mode
        for cmd in command_set:
            output = net_conn.send_command(cmd)
            # print(f"Output for '{cmd}':\n{output}\n")
            output_strings.append(output)
    except Exception as e:
        print(f"Error connecting to {TARGET_HOST} via netgate: {e}")
        return None
    finally:
        if net_conn:
            net_conn.disconnect()
        if chan:
            chan.close()
    return output_strings



def main():
    hosts_and_port_channels = []
    hosts_output = []
    target_hosts = load_hosts('hosts.txt')  
    command_set = ['sh vlan id 346', 'sh etherchan sum']
    jump_client = create_jump_client()
    try:
        for target in target_hosts:
            output_strings = connect_to_target_via_tunnel(jump_client, target, command_set)
            if output_strings:
                hosts_output.append((target, output_strings))              
            else:
                continue
    finally:
        try:
            jump_client.close()
        except Exception as e:
            print(f"Error closing jump client: {e}")    
            pass
    #validate output
    for target, output_strings in hosts_output:
       
        if vlan_present(output_strings[0]):
            print('Vlan346 is present')
            continue
        else:           
            channel_ids = get_port_channel_ids(output_strings[1])            
            if channel_ids:
                print((target, channel_ids))
                write_tuple('hosts_and_channels.txt', (target, channel_ids))                            
                # config_string = add_vlan(346, "TOTP", channel_ids[1])
                # print(config_string)                   
            else:
                print("No port channels found")
main()
