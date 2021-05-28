import socket, select, string, sys, tqdm, os

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

def create_client_socket(host_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    try :
	    s.connect((host_port[0], host_port[1]))
    except :
	    print("Unable to connect")
	    exit()
	
    print("Connected to remote host")

    return s

def create_server_socket(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server_address = ('localhost', port)
    server.bind(server_address)
    server.listen(5)
    return server

def execute_command(client_socket, msg):
    commands = msg.split()
    if commands[0] == "telnet":
        if commands[1] == "exec":
            if client_socket:
                client_socket.send(msg.encode())
            else:
                print("Not connected to a server!")
        elif commands[1] == "send":
            if client_socket:
                client_socket.send(commands[2].encode())
                print(f"Message sent to server {client_socket.getpeername()}")
            else:
                print("Not connected to a server!")
        elif commands[1] == "-e":
            if commands[2] == "send":
                if client_socket:
                    client_socket.send(commands[3].encode())
                    print(f"Message sent to server {client_socket.getpeername()} with TLS encryption")
                else:
                    print("Not connected to a server!")
        elif commands[1] == "upload":
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
        elif socket.gethostbyname(commands[1]):
            return create_client_socket([commands[1], int(commands[2])])
    else:
        print(f"Unknown command {msg}!")
        return None
    return None

def telnet_start(server_socket, client_socket):
    sockets = [sys.stdin, server_socket]
    while 1:
        read_sockets, write_sockets, error_sockets = select.select(sockets, [], sockets)
		
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
                c = execute_command(client_socket, msg)
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
                else:
                    msg = data.decode()
                    commands = msg.split()
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