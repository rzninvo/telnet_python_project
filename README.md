# Creating Telnet Using TCP sockets and P2P connections(Python)
This is a project for implementing telnet with python using basic socket programming.

## Notes:
* Supports port scanning for a given range of IPs.
* Supports encrypting and decrypting a message with OpenSSL AES encryption.
* Supports uploading files between clients localy and over the Internet.
* Supports connection to none local hosts.
* Has a log.txt file which records data being sent between clients for the sender.
* Has a database which records all the commands sent over the telnet protocol.
* Uses [PonyORM](https://ponyorm.org/) for database managements.
* Uses [tqdm](https://pypi.org/project/tqdm/) for fancy file_transfer progress bar.
* IMPORTANT: this code DOES NOT WORK ON WINDOWS, because it uses other file_descriptors besides sockets in it's selecter( for unblocking purposes).
## Program Initialization:
	$ Python3 telnet_client.py
After running the code the program waits for you to decide if you want to scan some IPs or start your telnet server.
## Scan:
  ```
  scan
  ```
  Simply writing scan will begin the process for scanning IPs. The rest is pretty easy to follow.
## Telnet Initialization:
  ```
  telnet [port]
  ```
  To start your telnet server you need to give an open port.
## Telnet; Connecting to a host:
  ```
  telnet [ip or hostname] [port]
  ```
  To connect to a host as a client, enter the hostname or ip and also the port on which you want to connect to the host.
## Telnet; sending a basic message:
  ```
  telnet send [your_message]
  ```
  **NOTE: You should first connect to a host as a client in order to send a message to them.**
## Telnet; sending an encrypted message:
  ```
  telnet -e send [your_message]
  ```
  **NOTE: You should first connect to a host as a client in order to send a message to them.**
## Telnet; uploading a file:
  ```
  telnet upload [file_path]
  ```
  **NOTE: You should first connect to a host as a client in order to send a message to them.**
## Telnet; getting the command records:
  ```
  telnet history db
  ```
  Shows all the commands that you've entered.
## Telnet; getting the sent data log:
  ```
  telnet history log
  ```
  Shows all the data that you've sent to your client.
## Telnet; executing a python code on your host:
  ```
  telnet exec [python_code]
  ```
  **NOTE: You should first connect to a host as a client in order to send a message to them.**
## Telnet; exiting the program
  ```
  telnet quit
  ```
