import socket, select, string, sys

def get_command():
    ip_list = []
    while (1):
	    inp = sys.stdin.readline()
        command = inp.split()
        
        if len(command) == 3:
            if command == "telnet":
                host = command[1]
                port = int(command[2])
                break;
            else: 
                print("Unknown command! Please try again")

        if inp == "scan":
            print("Please enter your ips (Put a single zero for ending the list)")
            while (1):
                ip = stdin.readline()
                if ip == 0:
                    break
                ip_list.append(ip)

    return [host, port, ip_list]

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
                result = s.connect_ex((target,port))
                if result == 0:
                    print("    Port " + port + " is open")
                s.close()
    else:
        print("Error: ip_list empty!")


if __name__ == "__main__":
    host_port,ip_list = get_command()
    scan_ports(ip_list)
	#s = create_socket(host_port)
    #telnet_start(s)
    