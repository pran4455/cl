import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print("Received:", msg)
        except:
            break

def start_client(host='localhost', port=5000):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    print("Connected to server.")
    print("You can start communicating.Type exit to quit:")
    while True:
        msg = input()
        if msg.lower() == "exit":
            break
        client.send(msg.encode())
    client.close()

if __name__ == "__main__":
    start_client()
