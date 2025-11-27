import socket
import pickle

class DataObject:
    def __init__(self, name, values):
        self.name = name
        self.values = values

def start_server(host='localhost', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    client_socket, addr = server_socket.accept()
    print(f"Connected to {addr}")

    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break

            received_obj = pickle.loads(data)
            print(f"Received object from {received_obj.name} with values: {received_obj.values}")

            total = sum(received_obj.values)
            response = f"Hello {received_obj.name}, sum is {total}"

            client_socket.sendall(pickle.dumps(response))

        except Exception as e:
            print("Error:", e)
            break

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
