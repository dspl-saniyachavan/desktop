import socket,ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

conn = context.wrap_socket(socket.socket(socket),server_hostname='localhost')
conn.connect(('localhost',8443))
try:
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break
        conn.sendall(msg.encode())
        print(conn.recv(1024).decode())
finally:
    conn.close()