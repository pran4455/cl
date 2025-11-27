import socket
import threading

clients = []

def handle_client(client_socket, addr):
    print(f"Client connected: {addr}")
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(f"{addr}: {msg}")
            broadcast(msg, client_socket)
        except:
            break
    client_socket.close()
    clients.remove(client_socket)

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                pass

def start_server(host='localhost', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server running on {host}:{port}")
    while True:
        client_socket, addr = server_socket.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    start_server()
