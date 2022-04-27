import socket
from utils import *

def connect_to_server(host, port):
    print("正在连接到服务端")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("连接成功！")
    return client


def main():
    ip_port = input("客户端启动，请输入服务端地址，格式\"host:port\"(英文冒号),默认本机:")
    if len(ip_port) == 0:
        ip_port = "localhost:9000"
    try:
        host, port = ip_port.split(":")
        port = int(port)
    except Exception as e:
        print("输入错误，" + repr(e))
        return

    client = connect_to_server(host, port)

    while True:
        try:
            mode = input("请选择模式(1:发送文件，2:接收文件，3：关闭连接):")
            if mode == "1":
                data = {"type": "c2s"}
                send_json(client, data)
                send(client)
            elif mode == "2":
                data = {"type": "s2c"}
                send_json(client, data)
                receive(client,save_path)
            elif mode == "3":
                data = {"type": "close"}
                send_json(client, data)
                break
            else:
                print("输入错误，请重新输入")
        except ConnectionAbortedError:
            print("连接中断")
            break
        except FunctionTimedOut:
            print("对方无响应")
            break
    client.close()



if __name__ == "__main__":
    save_path = input("请输入保存路径（默认当前路径）:")
    save_path = save_path if len(save_path) != 0 else os.getcwd()
    main()
