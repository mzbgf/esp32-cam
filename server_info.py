import requests

server_cidr = '192.168.31.11/24'
server_port = 9999

local_cidr = '192.168.0.164/24'

def get_netmask_4(length = 0):
    netmask = list()
    for i in range(4):
        x = 0
        for j in range(8):
            x <<= 1
            if length > 0:
                length -= 1
                x |= 1
        netmask.append(x)
    return netmask

local_ip, local_len = local_cidr.split('/')
local_ip = [ int(x) for x in local_ip.split('.') ]
local_netmask = get_netmask_4(int(local_len))
ip1 = [ x & y for x, y in zip(local_ip, local_netmask) ]

server_ip, server_len = server_cidr.split('/')
server_ip = [ int(x) for x in server_ip.split('.') ]
server_netmask = get_netmask_4(int(server_len))
ip2 = [ x | y for x, y in zip(server_ip, server_netmask) ]

local_server_ip = [ x | y ^ z for x, y, z in zip(ip1, ip2, server_netmask) ]

print(server_ip)
print(local_ip)
print(local_server_ip)