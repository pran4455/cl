import socket

def start_server(host='localhost', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))

    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")

    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        print(f"Received: {data}")

        try:
            numbers = list(map(int, data.strip().split()))
            total = sum(numbers)
            response = f"Sum: {total}"
        except ValueError:
            response = "Invalid input. Send space-separated integers."

        client_socket.sendall(response.encode())

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
