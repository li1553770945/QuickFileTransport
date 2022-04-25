import socket
from utils import *

def init_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"
    server.bind((host, port))
    server.listen(1)
    return server

if __name__ == "__main__":

    port = input("请输入端口（默认9000）:")
    save_path = input("请输入保存路径（默认当前路径）:")
    save_path = save_path if len(save_path) != 0 else os.getcwd()
    if len(port) == 0:
        port = 9000
    else:
        try:
            port = int(port)
        except:
            port = 9000
    server = init_server(port)

    while True:
        print('开始监听')
        client, addr = server.accept()
        print("接受一个新连接:".format(str(addr)))

        while True:
            message = receive_json(client)
            if message['type'] == "c2s":
                print("进入接收模式")
                receive(client,save_path)
            elif message['type'] == "s2c":
                print("进入发送模式")
                send(client)
            elif message['type'] == "close":
                print("关闭连接")
                break

        client.close()
