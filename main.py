import os
from dotenv import load_dotenv
import paramiko
from netmiko import ConnectHandler

load_dotenv()

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

def connect_to_target_via_tunnel(jump_client, TARGET_HOST):
    command_set = load_command_set('show_ints.txt')
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
            print(f"Output for '{cmd}':\n{output}\n")
    finally:
        if net_conn:
            net_conn.disconnect()
        if chan:
            chan.close()
    
def load_command_set(file_path):
    with open(file_path, 'r') as f:
        commands = [line.strip() for line in f if line.strip()]
    return commands

def main():
    target_hosts = ["172.16.224.215"]
    jump_client = create_jump_client()
    try:
        for target in target_hosts:
            connect_to_target_via_tunnel(jump_client, target)
    finally:
        try:
            jump_client.close()
        except Exception as e:
            print(f"Error closing jump client: {e}")    
            pass

main()

