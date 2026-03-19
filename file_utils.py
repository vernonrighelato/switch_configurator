def load_command_set(file_path):
    with open(file_path, 'r') as f:
        commands = [line.strip() for line in f if line.strip()]
    return commands

def read_from_file(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    return data

def write_to_file(file_path, data):
    with open(file_path, 'a') as f:
        f.write(data)

def write_tuple(filepath, tuple):
    with open(filepath, 'a') as f:
        f.write(str(tuple)+'\n')

def load_hosts(file_path):
    data = read_from_file(file_path)
    hosts = [data.split()[0] for data in data.splitlines()  if data.strip()]
    return hosts