from file_utils import *

int_data = read_from_file('output.txt')
data_lines = int_data.splitlines()
switches = []
ints = []
for line in data_lines:    
    if line.startswith('Interface'):
        switches.append([i for i in ints])
        ints = []
    else:
        ints.append(line.strip())

# for s in switches:
#     for line in s:
#         # print(line)
#     # print('------------------\n')

# get the mgmt address of each switch and store them in a list
mgmt_addresses = []
for s in switches:
    for line in s:
        if line.startswith('Vlan99'):
            mgmt_addresses.append(line.split()[1])

# get the hostnames from the hosts.txt file and store them in a list
hosts_data = read_from_file('all_hosts.txt')
hosts = [line.split() for line in hosts_data.splitlines() if line]

hosts_with_more_than_one_ip = []
for address in mgmt_addresses:
    for host in hosts:
        if address in host:
            hosts_with_more_than_one_ip.append(host)

for h in hosts_with_more_than_one_ip:
    if 'acc' in h[1] or 'cat' in h[1]:    
        print(h)