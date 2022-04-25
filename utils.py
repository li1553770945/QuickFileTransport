import os
import json

PACKAGESIZE = 1024*1024

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

    message = {"type":"begin","size":total_size,"name":file_name}
    send_json(client,message)
    size = 0
    with open(file,"rb") as f:
        last_per = 0
        while size < total_size:
            file_data = f.read(PACKAGESIZE)
            client.send(file_data)
            size += PACKAGESIZE
            per = size / total_size
            if per - last_per > 0.01:
                last_per = per
                os.system("cls")
                print("已发送{}字节，共{}字节，进度{:.2f}%".format(size,total_size,per*100))
    print("发送完成！")


def receive(client,save_path):
    message = receive_json(client)
    if message["type"] == "cancel":
        print("取消传输")
        return
    elif message["type"] == "begin":
        name = message["name"]
        print(name)
        total_size = message["size"]
        print("开始接收，文件名：{},总大小{}".format(name,total_size))
    else:
        return
    size = 0
    print()
    with open(os.path.join(save_path,name), 'wb') as file:
        last_per = 0
        while size < total_size:
            value = total_size - size
            if value > PACKAGESIZE:
                getdata = client.recv(PACKAGESIZE)
            else:
                getdata = client.recv(value)
            file.write(getdata)
            size += len(getdata)
            per = size / total_size
            if per-last_per > 0.01:
                last_per = per
                os.system("cls")
                print("已接收{}字节，共{}字节，进度{:.2f}%".format(size,total_size,per*100))
    print("接收完成")

def receive_json(client):
    message_bytes = client.recv(128)
    size = len(message_bytes)
    while size < 128:
        message_bytes += client.recv(128)
    message = json.loads(message_bytes.decode("utf8"))
    return message


def send_json(client, message):
    json_string = json.dumps(message).encode('utf-8')
    json_string += (" " * (128 - len(json_string))).encode("utf8")
    client.send(json_string)