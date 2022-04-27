import datetime
import os
import json
import threading
from queue import Queue
import socket
from func_timeout import FunctionTimedOut, func_timeout

PACKAGESIZE = 1024 * 1024

def send(client):
    file = input("请输入文件路径：")
    if not os.path.exists(file) or not os.path.isfile(file):
        print("文件不存在或者为文件夹")
        message = {"type": "cancel"}
        send_json(client, message)
        return

    total_size = os.path.getsize(file)
    if total_size <= 0:
        print("文件大小为0")
        message = {"type": "cancel"}
        send_json(client, message)
        return

    file_name = os.path.split(file)[-1]

    message = {"type": "begin", "size": total_size, "name": file_name}
    send_json(client, message)
    print("已发送传输请求，等待回应...")
    message = receive_json(client,60)
    start_size = message['start_size']
    if start_size:
        print("启用断点续传，从{}字节开始".format(start_size))
    size = start_size
    print("开始传输")
    with open(file, "rb") as f:
        last_per = 0
        while size < total_size:
            file_data = f.read(PACKAGESIZE)
            client.send(file_data)
            size += PACKAGESIZE
            per = size / total_size
            if per - last_per > 0.01:
                last_per = per
                os.system("cls")
                print("已发送{}字节，共{}字节，进度{:.2f}%".format(size, total_size, per * 100))
    print("发送完成！")


def receive(client, save_path):
    message = receive_json(client,60)
    if message["type"] == "cancel":
        print("取消传输")
        return
    elif message["type"] == "begin":
        name = message["name"]
        total_size = message["size"]
        print("准备开始接收，文件名：{},总大小{}".format(name, total_size))
        print("正在检验本地文件...")
        local_size = 0
        if os.path.exists(os.path.join(save_path, name)):
            local_size = os.path.getsize(os.path.join(save_path, name))

        if local_size:
            print("已存在同名文件,且大小为{}字节，是否启用断点续传？（Y:是，其他：否），5秒后自动选择是:".format(local_size))
            continue_from_break = "Y"
            try:
                continue_from_break = func_timeout(5, lambda: input())
            except FunctionTimedOut:
                print("选择默认")
            continue_from_break = True if continue_from_break == "Y" else False
        else:
            continue_from_break = True

        if continue_from_break:
            send_json(client, {"start_size": local_size})
        else:
            send_json(client, {"start_size": 0})
    else:
        return
    size = 0
    print("开始传输")
    with open(os.path.join(save_path, name), 'wb') as file:
        last_per = 0
        last_not_zero = datetime.datetime.now()
        while size < total_size:
            value = total_size - size
            if value > PACKAGESIZE:
                getdata = func_timeout(60,client.recv,args=(PACKAGESIZE,))
            else:
                getdata = func_timeout(60,client.recv,args=(value,))
            if len(getdata):
                last_not_zero = datetime.datetime.now()
                file.write(getdata)
                size += len(getdata)
                per = size / total_size
                if per - last_per > 0.01:
                    last_per = per
                    os.system("cls")
                    print("已接收{}字节，共{}字节，进度{:.2f}%".format(size, total_size, per * 100))
            elif datetime.datetime.now() - last_not_zero > datetime.timedelta(seconds=60):
                raise FunctionTimedOut


    print("接收完成")


def receive_func(client):
    message_bytes = client.recv(128)
    size = len(message_bytes)
    while size < 128:
        message_bytes += client.recv(128)
    return message_bytes


def receive_json(client, timeout=3600):
    message_bytes = func_timeout(timeout, receive_func,args=(client,))
    message = json.loads(message_bytes.decode("utf8"))
    return message


def send_json(client, message):
    json_string = json.dumps(message).encode('utf-8')
    json_string += (" " * (128 - len(json_string))).encode("utf8")
    client.send(json_string)
