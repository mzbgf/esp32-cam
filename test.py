# from logging import debug as print
import struct
import socket
import time

def udp_bind(ip, port):
    print((ip, port))
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind((ip, port))
    return udp

bind_ip = '0.0.0.0'
multicast_socket = udp_bind(bind_ip, 9999)

multicast_ip = '239.2.3.54'
multicast_group = (multicast_ip, 9999)
multicast_socket.setblocking(False)
multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

multicast_socket.setsockopt(
    socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
    socket.inet_aton(multicast_ip) + socket.inet_aton(bind_ip)
)
try:
    data = struct.pack('!f', time.time())
    print("Sending data: {!r}".format(data))
    sent = multicast_socket.sendto(data, multicast_group)
    for i in range(1):
        try:
            print('\nwaiting to receive message')
            data, address = multicast_socket.recvfrom(1024)
            print('received {} bytes from {}'.format(len(data), address))
            print('received data: {!r}'.format(data))
        except Exception as e:
            print(e)
except Exception as e:
    print(e)
finally:
    pass
    # multicast_socket.setsockopt(
    #     socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
    #     socket.inet_aton(multicast_ip) + socket.inet_aton(bind_ip)
    # )