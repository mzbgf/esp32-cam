from config import *
import socket
import camera
import webrepl
from time import sleep

token = 'esp'
udp_port = 0
tcp_port = 9998
bind_ip = '0.0.0.0'
broadcast_addr = ('255.255.255.255', 9999)
data = {
    'token': token,
    'port': tcp_port
}

def BroadCast():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind((bind_ip, udp_port))
    try:
        while True:
            udp.sendto(
                str(data).encode(),
                broadcast_addr
            )
            sleep(2)
            yield
    except Exception as e:
        print(e)
    finally:
        udp.close()

broadcast = BroadCast().__next__

def GetAddress():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((bind_ip, tcp_port))
    server_socket.settimeout(1)
    server_socket.listen(3)
    try:
        while True:
            try:
                print('broadcast')
                broadcast()
                print('accepting...')
                client_socket, (ip, _) = server_socket.accept()
                print('acceptted from: ', ip)
                msg = client_socket.recv(1024)
                data = eval(msg.decode())
                if data['token'] != token:
                    raise Exception(f"data: {msg.decode()}")
                addr = (ip, data['port'])
                client_socket.close()
                yield addr
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    finally:
        server_socket.close()

get_addr = GetAddress().__next__

def send_img(address = None):
    while True:
        try:
            print('getting server_address..')
            server_address = get_addr() if address is None else address
            print('connecting to: ', server_address)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(3)
            client_socket.connect(server_address)
            print('connected.')
            while True:
                sleep(0.1)
                buf = camera.capture()
                if buf == False:
                    print('capture failled')
                    continue
                buf_len = len(buf)
                try:
                    client_socket.sendall(str.encode('%-16s' % buf_len))
                    _ = client_socket.sendall(buf)
                except Exception as e:
                    print(e)
                    break
        except Exception as e:
            print(e)

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

