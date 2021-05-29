import socket, string, sys, tqdm, os, select as net_select
from datetime import datetime
from db_orm import *
from Crypto.Cipher import AES
import base64
import Padding

key='telnet'
salt='241fa86763b85341'


def get_key_and_iv(password, salt, klen=32, ilen=16, msgdgst='md5'):

    mdf = getattr(__import__('hashlib', fromlist=[msgdgst]), msgdgst)
    password = password.encode('ascii', 'ignore')
    salt = bytearray.fromhex(salt)

    try:
        maxlen = klen + ilen
        keyiv = mdf((password + salt)).digest()
        tmp = [keyiv]
        while len(tmp) < maxlen:
            tmp.append( mdf(tmp[-1] + password + salt).digest() )
            keyiv += tmp[-1]
        key = keyiv[:klen]
        iv = keyiv[klen:klen+ilen]
        return key, iv
    except UnicodeDecodeError:
         return None, None

def encrypt(plaintext,key, mode,salt):
	key,iv=get_key_and_iv(key,salt)
	
	encobj = AES.new(key,mode,iv)
	return(encobj.encrypt(plaintext.encode()))

def decrypt(ciphertext,key, mode,salt):
	key,iv=get_key_and_iv(key,salt)
	encobj = AES.new(key,mode,iv)
	return(encobj.decrypt(ciphertext))

def get_command():
    ip_list = []
    port = 0
    while (1):
        inp = input()
        if inp == "scan":
            print("Please enter your ips (Put a single 0 for ending the list)")
            while (1):
                ip = input()
                if ip == "0":
                    return [port, ip_list, inp]                
                ip_list.append(socket.gethostbyname(ip))
        else:
            command = inp.split()
            if len(command) == 2:
                if command[0] == "telnet":
                    port = int(command[1])
                    return [port, ip_list, command[0]]
                else:
                    print("Unknown command! Please try again")

def create_client_socket(host_port, server_socket):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try :
	    s.connect((host_port[0], host_port[1]))
    except :
	    print("Unable to connect")
	    exit()
	
    print("Connected to remote host")
    with db_session:
        if not select(i for i in Client if i.client_ip_port == f"127.0.0.1, {server_socket.getsockname()[1]}"):
            Client(client_ip_port= f"127.0.0.1, {server_socket.getsockname()[1]}", server_ip_port= f"{socket.gethostbyname(host_port[0])}, {host_port[1]}")
    return s

def create_server_socket(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server_address = ('localhost', port)
    server.bind(server_address)
    server.listen(5)
    with db_session:
        try:
            if not select(i for i in Server if i.server_ip_port == f"127.0.0.1, {port}"):
                Server(server_ip_port= f"127.0.0.1, {port}")
        except:
            None
    return server

def execute_command(client_socket, server_socket, msg):
    with db_session:
        if client_socket:
            Telnet_History_System(server_ip_port= f"{client_socket.getsockname()[0]}, {client_socket.getsockname()[1]}", 
                    client_ip_port= f"{server_socket.getsockname()[0]}, {server_socket.getsockname()[1]}",
                    date_time= datetime.now(),
                    command= msg)
    commands = msg.split(" ", 2)
    if commands[0] == "telnet":
        if commands[1] and commands[1] == "exec":
            if client_socket:
                client_socket.send(msg.encode())
                print(f"Execution command sent to server {client_socket.getpeername()}")
            else:
                print("Not connected to a server!")
        elif commands[1] and commands[1] == "send":
            if client_socket:
                client_socket.send(commands[2].encode())
                with open("log.txt", "a") as f:
                    f.write(f"{datetime.now()} || Client {server_socket.getsockname()} sending data {commands[2].encode()} to Server {client_socket.getsockname()}\n")
                f.close()
                print(f"Message sent to server {client_socket.getpeername()}")
            else:
                print("Not connected to a server!")
        elif commands[1] and commands[1] == "-e":
            commands = msg.split(" ", 3)
            if commands[2] and commands[2] == "send":
                if client_socket:
                    plaintext = commands[3]
                    plaintext = Padding.appendPadding(plaintext,mode='CMS')
                    ciphertext = encrypt(plaintext,key,AES.MODE_CBC,salt)
                    ctext = b'Salted__' + bytearray.fromhex(salt) + ciphertext
                    client_socket.send(ctext)
                    with open("log.txt", "a") as f:
                        f.write(f"{datetime.now()} || Client {server_socket.getsockname()} sending data {ctext} to Server {client_socket.getsockname()}\n")
                    f.close()
                    print(f"Message sent to server {client_socket.getpeername()} with TLS encryption")
                else:
                    print("Not connected to a server!")
            else:
                print(f"Unknown command {msg}!")
        elif commands[1] and commands[1] == "upload":
            if os.path.isfile(commands[2]):
                if client_socket:
                    filesize = os.path.getsize(commands[2])
                    filename = commands[2]
                    client_socket.send(f"FILE_REQUEST|{filename}|{filesize}".encode())
                    timer = 0
                    state = 0
                    while (1):
                        data = (client_socket.recv(4056)).decode()
                        if data == "FILE_UPLOAD_REQUEST_ACCEPTED":
                            print("Starting file transfer...")
                            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                            with open(filename, "rb") as f:
                                flag = 0
                                while not flag:
                                    try:
                                        fdata = f.read(4096)
                                        client_socket.send(fdata)
                                        progress.update(len(fdata))
                                        if not fdata:
                                            flag = 1
                                            break
                                    except Exception as e:
                                        None
                            progress.close()
                            f.close()
                            state = 1
                            break
                        elif data == "FILE_UPLOAD_REQUEST_DENIED":
                            print(f"File transfer failed for server reason{data}")
                            break
                        else:
                            timer = timer + 1
                        if timer == 10000:
                            print("File request timed out!")
                            state = 0
                            break
                    if state:
                        print("File sent successfully!")
                    else:
                        print("File could not be sent!")
                else:
                    print("Not connected to a server!")
            else:
                print("File does not exist!")
        elif commands[1] and commands[1] == "history":
            if commands[2] and commands[2] == "log":
                with open("log.txt", "r") as f:
                    print (f.read())
                f.close()
            elif commands[2] and commands[2] == "db":
                with db_session:
                    Telnet_History_System.select().show()
            else:
                print(f"Unknown command {msg}!")
        elif commands[1] and commands[1] == "quit":
            exit()
        elif commands[1] and socket.gethostbyname(commands[1]):
            return create_client_socket([commands[1], int(commands[2])], server_socket)
        else:
            print(f"Unknown command {msg}!")    
    else:
        print(f"Unknown command {msg}!")
    return None

def telnet_start(server_socket, client_socket):
    sockets = [sys.stdin, server_socket]
    while 1:
        read_sockets, write_sockets, error_sockets = net_select.select(sockets, [], sockets)
		
        for sock in read_sockets:   
            if sock == client_socket:
                data = sock.recv(4096)
                if not data :
                    print(f"Connection to {sock.getpeername()} closed")
                    sockets.remove(sock)
                else:
                    print(f"Received some data from server {sock.getpeername()}")
                    print(f"Server: {data.decode()}")
            elif sock == server_socket:
                connection, client_address = sock.accept()
                print("New connection from ", client_address)
                connection.setblocking(0)
                sockets.append(connection)
            elif sock == sys.stdin:
                msg = input()
                c = execute_command(client_socket, server_socket, msg)
                if client_socket == None and c:
                    client_socket = c
                    sockets.append(client_socket)
                elif client_socket != None and c:
                    print(f"Client socket is already in use by {client_socket.getpeername()}")

            else:
                data = sock.recv(4096)
                if not data :
                    print(f"Closing {sock.getpeername()} after reading no data!")
                    sockets.remove(sock)
                    sock.close()
                elif data[0:8].decode() == 'Salted__':
                    print(f"Received ecrypted OpenSSL AES data {data} from client {sock.getpeername()}")
                    ciphertext = data[len(b'Salted__' + bytearray.fromhex(salt)):]
                    plaintext = decrypt(ciphertext,key,AES.MODE_CBC,salt)
                    plaintext = Padding.removePadding(plaintext.decode(),mode='CMS')
                    print(f"Decrypted {plaintext} from client {sock.getpeername()}")
                else:
                    msg = data.decode()
                    commands = msg.split(" ", 2)
                    file_com = msg.split("|")
                    if commands[0] ==  "telnet" and commands[1] == "exec":
                        print(f"Executing {commands[2]} from client {sock.getpeername()}")
                        try:
                            exec(commands[2])
                        except Exception:
                            print(Exception)
                    elif file_com[0] == "FILE_REQUEST":
                        filename = file_com[1]
                        filesize = int(file_com[2])
                        if filename and filesize:
                            sock.send("FILE_UPLOAD_REQUEST_ACCEPTED".encode())
                            filename = os.path.basename(filename)
                            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                            fz = 0
                            with open(filename, "wb") as f:
                                state = 0
                                while not state:
                                    try:
                                        fdata = sock.recv(4096)
                                        f.write(fdata)
                                        progress.update(len(fdata))
                                        fz = fz + len(fdata)
                                        if fz >= filesize:
                                            state = 1
                                            break
                                    except Exception as e:
                                        None
                            progress.close()
                            f.close()
                            print("File recieved successfuly")
                        else:
                            sock.send("FILE_UPLOAD_REQUEST_DENIED".encode())
                    else:
                        print(f"Received {data.decode()} from client {sock.getpeername()}")
                    
        for sock in error_sockets:
            print(f"Handling exceptional condition for client {sock.getpeername()}")
            sockets.remove(sock)
            sock.close()    

def scan_ports(ip_list):
    if ip_list:
        for ip in ip_list:
            print("Scanning host " + ip + " ...")
            for port in range(1,65535):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)
                result = s.connect_ex((ip,port))
                if result == 0:
                    print("    Port " + str(port) + " is open")
                s.close()
    else:
        print("Error: ip_list empty!")

if __name__ == "__main__":
    client_socket = None
    data = get_command()
    if data[2] == "scan":
        scan_ports(data[1])
    if data[2] == "telnet":
        server_socket = create_server_socket(data[0])
        telnet_start(server_socket, client_socket)