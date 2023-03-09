import selectors
import socket
import datetime

HOST = 'айпи'
PORT = 3544

sel = selectors.DefaultSelector()
clients = {}

def accept_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")
    client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ, data=handle_client)

    clients[client_socket] = {"address": client_address}

def handle_client(client_socket):
    recv_data = client_socket.recv(1024)
    if recv_data:
        message = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {clients[client_socket]['address'][0]}: {recv_data.decode()}"
        print(message)
        broadcast_message(message, client_socket)
    else:
        print(f"Closed connection from {clients[client_socket]['address']}")
        sel.unregister(client_socket)
        client_socket.close()
        del clients[client_socket]

def broadcast_message(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode())
            except:
                print(f"Error broadcasting message to {clients[client_socket]['address']}")


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(88)
    server_socket.setblocking(False)
    sel.register(server_socket, selectors.EVENT_READ, data=accept_connection)
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)