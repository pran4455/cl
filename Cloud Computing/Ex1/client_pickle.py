import socket
import pickle

class DataObject:
    def __init__(self, name, values):
        self.name = name
        self.values = values

def start_client(host='localhost', port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        name = input("Enter your name (or 'exit' to quit): ")
        if name.lower() == 'exit':
            break

        try:
            nums = input("Enter space-separated numbers: ")
            values = list[int](map[int](int, nums.strip().split()))
            obj = DataObject(name, values)

            client_socket.sendall(pickle.dumps(obj))

            response = client_socket.recv(4096)
            message = pickle.loads(response)
            print("Server response:", message)

        except Exception as e:
            print("Error:", e)

    client_socket.close()

if __name__ == "__main__":
    start_client()
