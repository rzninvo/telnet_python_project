import socket, select, string, sys

def get_command():
    ip_list = []
    host = ""
    port = 0
    while (1):
        inp = input()
        if inp == "scan":
            print("Please enter your ips (Put a single zero for ending the list)")
            while (1):
                ip = input()
                if ip == "0":
                    return [host, port, ip_list, inp]                
                ip_list.append(socket.gethostbyname(ip))
        else:
            command = inp.split()

            if len(command) == 3:
                if command[0] == "telnet":
                    host = command[1]
                    port = int(command[2])
                    return [host, port, ip_list, command[0]]
                else:
                    print("Unknown command! Please try again")

def create_socket(host_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    try :
	    s.connect((host_port[0], host_port[1]))
    except :
	    print("Unable to connect")
	    sys.exit()
	
    print("Connected to remote host")

    return s

def telnet_start(s):
    while 1:
	    sockets = [sys.stdin, s]
	    read_sockets, write_sockets, error_sockets = select.select(sockets , [], [])
		
	    for sock in read_sockets:
		    if sock == s:
			    data = sock.recv(4096)
			    if not data :
				    print("Connection closed")
				    sys.exit()
			    else :
				    sys.stdout.write(data)
		    else :
			    msg = sys.stdin.readline()
			    s.send(msg)

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
    data = get_command()
    if data[3] == "scan":
        scan_ports(data[2])
    if data[3] == "telnet":
        s = create_socket(data)
        telnet_start(s)