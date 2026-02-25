import socket, ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="certificate.pem" , keyfile="key.pem")
bindsocket = socket.socket()
bindsocket.bind(('0.0.0.0' ,8443))
bindsocket.listen(5)
print("server listening")

while True:
    newsocket,addr = bindsocket.accept()
    conn = context.wrap_socket(newsocket,server_side=True)
    print("connection from {addr}")
    try:
        while True:
            data=conn.recv(1024)
            if not data:
                break
            print("client",data.decode())
            conn.sendall(b"Server echo: "+data)
    finally:
        conn.close()
