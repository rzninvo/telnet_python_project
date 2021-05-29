from pony.orm import *
from datetime import datetime
import mysql.connector
from getpass import getpass

db = Database()

class Server(db.Entity):
    server_ip_port = PrimaryKey(str, 60)

class Client(db.Entity):
    client_ip_port = PrimaryKey(str, 60)
    server_ip_port = Required(str, 60)

class Telnet_History_System(db.Entity):
    id = PrimaryKey(int, auto=True)
    server_ip_port = Required(str, 60)
    client_ip_port = Required(str, 60)
    date_time = Required(datetime)
    command = Required(str, 255)

username = getpass("Database user:")
password = getpass("Database password:")

db.bind(provider="mysql", host="localhost", user=username, passwd=password, db="telnet_history")
db.generate_mapping(create_tables=True)

""" with db_session:
    Server.select().show()
    Client.select().show()
    Telnet_History_System.select().show() """