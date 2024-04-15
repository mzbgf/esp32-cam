import requests, time

class CIDR4:
    def __init__(self, cidr: str) -> None:
        self.cidr = cidr
        self.ip_str, len = cidr.split('/')
        self.netmask_int = int(len)
        self.ip_list = [ int(x) for x in self.ip_str.split('.') ]
        self.netmask_list = self.get_netmask()
        self.ip1_list = [ x & y for x, y in zip(self.ip_list, self.netmask_list)]
        self.ip2_list = [ x | y for x, y in zip(self.ip_list, self.netmask_list)]

    def get_netmask(self) -> list:
        netmask_list = list()
        for i in range(4):
            x = 0
            for j in range(8):
                x <<= 1
                if self.netmask_int > 0:
                    self.netmask_int -= 1
                    x |= 1
            netmask_list.append(x)
        return netmask_list
    
    def merge_ip(self, cidr) -> str:
        if isinstance(cidr, str):
            return self.merge_ip(CIDR4(cidr))
        else: # isinstance(cidr, CIDR4)
            merged_ip_str_list = [ str(x | y ^ z) for x, y, z in zip(self.ip1_list, cidr.ip2_list, cidr.netmask_list) ]
            merged_ip_str = '.'.join(merged_ip_str_list)
            return merged_ip_str

debug = True

local_cidr = '192.168.0.164/24'

if locals().get('debug'):
    print('debug mode')
    server_info = {
        "type": "tcp",
        "cidr": "192.168.31.11/24",
        "port": 9999
    }
else:
    api_url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/mzbgf/esp32-cam/main/api"
    while True:
        req = requests.get(api_url + "/static/server_info.json")
        if req.ok:
            break
        time.sleep(1)
    server_info = req.json()

server_type = server_info['type']
server_cidr = server_info['cidr']
server_port = server_info['port']

local_server_ip = CIDR4(local_cidr).merge_ip(server_cidr)

print(server_info)
print('local_cidr: ', local_cidr)
print(local_server_ip)