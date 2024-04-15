import socket
from time import sleep

token = 'esp'
bind_ip = '0.0.0.0'
tcp_port = 9999
udp_port = 9999
http_port = 8080
data = {
    'token': token,
    'port': tcp_port
}
def GetAddress():
    "from_broadcast_get_tmp_addr"
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.bind((bind_ip, udp_port))
    try:
        while True:
            try:
                msg, (ip, _) = udp.recvfrom(1024)
                data = eval(msg.decode())
                if data['token'] != token:
                    raise Exception(f"data: {msg.decode()}")
                addr = (ip, data['port'])
                yield addr
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    finally:
        udp.close()

get_addr = GetAddress().__next__

def send_addr():
    sleep(0.4)
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(3)
            server_address = get_addr()
            print('connecting to: ', server_address)
            client_socket.connect(server_address)
            print('sending...')
            client_socket.send(str(data).encode())
            print('sent.')
            client_socket.close()
        except Exception as e:
            print(e)

def receive_all(sock, count):
    buf = b''
    while count:
        recv_data_temp = sock.recv(count)
        if not recv_data_temp:
            return None
        buf += recv_data_temp
        count -= len(recv_data_temp)
    return buf

def receive_img(stream):
    sleep(0.3)
    import cv2, numpy as np
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((bind_ip, tcp_port))
    server_socket.listen(3)
    while True:
        try:
            print('acceptting...')
            client_socket, address = server_socket.accept()
            print('accepted from: ', address)
            while True:
                length = receive_all(client_socket, 16)
                if not length:
                    break
                length = int(length.decode())
                video_data = receive_all(client_socket, length)
                if not video_data:
                    break
                img_buffer_numpy = np.frombuffer(video_data, dtype=np.uint8)
                img_numpy = cv2.imdecode(img_buffer_numpy, cv2.IMREAD_COLOR)
                stream.set_frame(img_numpy)
        except Exception as e:
            print(e)
        else:
            client_socket.close()

def run_stream():
    from mjpeg_streamer import MjpegServer, Stream
    stream = Stream("my_camera")

    server = MjpegServer('0.0.0.0', http_port)
    server.add_stream(stream)
    server.start()
    
    return stream

if __name__ == '__main__':
    from threading import Thread
    stream = run_stream()
    task_receive_img = Thread(target=receive_img, args=(stream, ))
    task_send_addr = Thread(target=send_addr)
    tasks = [
        task_receive_img,
        task_send_addr
    ]

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()
