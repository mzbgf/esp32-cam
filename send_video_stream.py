from config import *
import socket
import camera
import webrepl
import requests
import time

# udp_port = 0
# bind_ip = '0.0.0.0'
# broadcast_addr = ('255.255.255.255', 9999)

api_url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/mzbgf/esp32-cam/main/api"

token = 'esp'
tcp_port = 9998

data = {
    'token': token,
    'port': tcp_port
}

# def BroadCast():
#     udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
#     udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     udp.bind((bind_ip, udp_port))
#     try:
#         while True:
#             udp.sendto(
#                 str(data).encode(),
#                 broadcast_addr
#             )
#             sleep(2)
#             yield
#     except Exception as e:
#         print(e)
#     finally:
#         udp.close()

# broadcast = BroadCast().__next__

# def GetAddress():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server_socket.bind((bind_ip, tcp_port))
#     server_socket.settimeout(1)
#     server_socket.listen(3)
#     try:
#         while True:
#             try:
#                 print('broadcast')
#                 broadcast()
#                 print('accepting...')
#                 client_socket, (ip, _) = server_socket.accept()
#                 print('acceptted from: ', ip)
#                 msg = client_socket.recv(1024)
#                 data = eval(msg.decode())
#                 if data['token'] != token:
#                     raise Exception(f"data: {msg.decode()}")
#                 addr = (ip, data['port'])
#                 client_socket.close()
#                 yield addr
#             except Exception as e:
#                 print(e)
#     except Exception as e:
#         print(e)
#     finally:
#         server_socket.close()

# get_addr = GetAddress().__next__

# def send_img(address = None):
#     while True:
#         try:
#             print('getting server_address..')
#             server_address = get_addr() if address is None else address
#             print('connecting to: ', server_address)
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.settimeout(3)
#             client_socket.connect(server_address)
#             print('connected.')
#             while True:
#                 sleep(0.1)
#                 buf = camera.capture()
#                 if buf == False:
#                     print('capture failled')
#                     continue
#                 buf_len = len(buf)
#                 try:
#                     client_socket.sendall(str.encode('%-16s' % buf_len))
#                     _ = client_socket.sendall(buf)
#                 except Exception as e:
#                     print(e)
#                     break
#         except Exception as e:
#             print(e)

if not locals().get('camera'): camera = None

class CIDR4:
    def __init__(self, cidr: str) -> None:
        self.cidr = cidr
        self.ip_str, netmask = cidr.split('/')
        try:
            netmask_int = int(netmask)
            self.netmask_list = self.get_netmask(netmask_int)
        except ValueError as e:
            self.netmask_list = [ int(x) for x in netmask.split('.') ]
        self.ip_list = [ int(x) for x in self.ip_str.split('.') ]
        self.ip1_list = [ x & y for x, y in zip(self.ip_list, self.netmask_list)]
        self.ip2_list = [ x | y for x, y in zip(self.ip_list, self.netmask_list)]

    def get_netmask(self, netmask_int = 0) -> list:
        netmask_list = list()
        for i in range(4):
            x = 0
            for j in range(8):
                x <<= 1
                if netmask_int > 0:
                    netmask_int -= 1
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

def get_server():
    request_times = 0
    while request_times < 3:
        req = requests.get(url=api_url + "/static/server_info.json", timeout=5)
        if req.ok:
            break
    return req.json()

def send_img(server_addr = None):
    if server_addr is None:
        server_info = get_server()

        server_type = server_info['type']
        server_cidr = server_info['cidr']
        server_port = server_info['port']

        local_server_ip = CIDR4(local_cidr).merge_ip(server_cidr)
        server_addr = (local_server_ip, server_port)
    
    def warp(socket):
        while True:
                time.sleep(0.1)
                buf = camera.capture()
                if buf == False:
                    print('capture failled')
                    continue
                buf_len = len(buf)
                try:
                    socket.sendall(str.encode('%-16s' % buf_len))
                    _ = socket.sendall(buf)
                except Exception as e:
                    print(e)
                    break
    
    if server_type == 'tcp':
        tcp_reconnect_times = 0
        while tcp_reconnect_times < 10:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(3)
                client_socket.connect(server_addr)
                print('connected.')
                warp(client_socket)
            except Exception as e:
                print(e)
            finally:
                tcp_reconnect_times += 1
    elif server_type == 'udp':
        pass

def main(mode = 0):
    """
    debug: mode=1 in main.py and mode=2 in test.py
    release: mode=0 in main.py
    """
    if mode == 0 or mode == 1:
        wifi_connect()
        webrepl.start(password='')
        if mode == 1: return
    try:
        camera_init()
        send_img()
    except Exception as e:
        print(e)
    finally:
        camera.deinit()

main(mode=0)

