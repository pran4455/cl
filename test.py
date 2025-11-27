#=================simple server==============

import pickle
import socket
from data_object import DataObject

host = '127.0.0.1'
port = 8000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print(f"Server listening on {host}:{port}")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        data = conn.recv(1024)
        if data:
            obj = pickle.loads(data)
            print("Received object:", obj.name, obj.values)
            response = f"DataObject '{obj.name}' with values {obj.values} received."
            conn.sendall(pickle.dumps(response))

class DataObject:
    def __init__(self, name, values):
        self.name = name
        self.values = values
 
# ==========client===============

import pickle
import socket 

from data_object import DataObject

host = '127.0.0.1'
port = 8000

data = DataObject("SampleData", [1, 2, 3, 4, 5])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    serialized_data = pickle.dumps(data)
    s.sendall(serialized_data)
    print("Data sent to server.")
    data_received = s.recv(1024)
    if data_received:   
        response = pickle.loads(data_received)
        print("Response from server:", response)    


# =====================server broadcast================

import socket
import threading

clients = []

def broadcast(msg, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(msg)
            except:
                clients.remove(client)

def handle_client(client_socket, addr):
    print(f"New connection from {addr}")
    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break
            broadcast(msg, client_socket)
        except:
            clients.remove(client_socket)
            break
    client_socket.close()

def main():
    host = '127.0.0.1'
    port = 9999
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print("Server listening on port", port)

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    main()

# ====================client broadcast================
import socket
import threading

def receive(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            print("\nReceived:", msg)
        except:
            break

def main():
    host = '127.0.0.1'
    port = 9999
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    threading.Thread(target=receive, args=(client,)).start()

    while True:
        msg = input("You: ")
        client.send(msg.encode())

if __name__ == "__main__":
    main()

# ==================RMI================

#calculator
import Pyro4

@Pyro4.expose
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b
    
#server.py
import Pyro4
from calculator import Calculator

daemon = Pyro4.Daemon()
uri = daemon.register(Calculator)
print(uri)
daemon.requestLoop()

#client.py
import Pyro4
uri = input("Enter the Calculator service URI: ")  # e.g., PYRO:obj_xxxxx@localhost:xxxx
calculator = Pyro4.Proxy(uri)
calculator.add(5, 3)
calculator.multiply(5, 3)
print("Addition Result:", calculator.add(5, 3)) 
print("Multiplication Result:", calculator.multiply(5, 3))


# ==================Ricart===============

import socket
import threading
import time

# Configuration
MY_PORT = 5001 # Change for each process
PROCESS_PORTS = [5001, 5002, 5003]

RECEIVED_REPLIES = set()

def listen():
    global RECEIVED_REPLIES
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', MY_PORT))
    server.listen()
    print(f"[{MY_PORT}] Listening for messages...")

    while True:
        conn, _ = server.accept()
        msg = conn.recv(1024).decode()

        if msg.startswith("REQUEST"):
            sender_port = int(msg.split(":")[1])
            print(f"[{MY_PORT}] Received REQUEST from {sender_port}")
            conn.send(f"REPLY:{MY_PORT}".encode())

        elif msg.startswith("REPLY"):
            sender_port = int(msg.split(":")[1])
            print(f"[{MY_PORT}] Received REPLY from {sender_port}")
            RECEIVED_REPLIES.add(sender_port)

        conn.close()

def request_cs():
    global RECEIVED_REPLIES
    RECEIVED_REPLIES = set()
    print(f"[{MY_PORT}] Requesting Critical Section...")

    for port in PROCESS_PORTS:
        if port != MY_PORT:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(('localhost', port))
                s.send(f"REQUEST:{MY_PORT}".encode())
                reply = s.recv(1024).decode()
                if reply.startswith("REPLY"):
                    sender_port = int(reply.split(":")[1])
                    print(f"[{MY_PORT}] Got REPLY from {sender_port}")
                    RECEIVED_REPLIES.add(sender_port)
            except Exception as e:
                print(f"[{MY_PORT}] Error connecting to {port}: {e}")
            finally:
                s.close()

    while len(RECEIVED_REPLIES) < len(PROCESS_PORTS) - 1:
        print(f"[{MY_PORT}] Waiting for replies: {RECEIVED_REPLIES}")
        time.sleep(0.5)

    print(f"[{MY_PORT}] Entering Critical Section...")
    time.sleep(2)
    print(f"[{MY_PORT}] Exiting Critical Section...")

def run():
    threading.Thread(target=listen, daemon=True).start()
    while True:
        input(f"[{MY_PORT}] Press Enter to request CS...")
        request_cs()

if __name__ == "__main__":
    run()

# =================Token================
import socket
import threading
import time

NEXT_PORT = {
    5001: 5002,
    5002: 5003,
    5003: 5001,
}

MY_PORT = 5001      # Change for each process
START_TOKEN = True  # Set True for one process to start the token

def listen(my_port):
    server = socket.socket()
    server.bind(('localhost', my_port))
    server.listen()
    print(f"[{my_port}] Listening for TOKEN...")

    while True:
        conn, _ = server.accept()
        msg = conn.recv(1024).decode()

        if msg == "TOKEN":
            print(f"[{my_port}] Received TOKEN.")
            enter_cs(my_port)
            send_token(NEXT_PORT[my_port])

        conn.close()

def enter_cs(my_port):
    print(f"[{my_port}] Entering Critical Section...")
    time.sleep(2)
    print(f"[{my_port}] Exiting Critical Section...")

def send_token(next_port):
    time.sleep(1)
    while True:
        try:
            s = socket.socket()
            s.connect(('localhost', next_port))
            s.send("TOKEN".encode())
            s.close()
            print(f"[{MY_PORT}] Token sent to {next_port}.")
            break
        except ConnectionRefusedError:
            print(f"[{MY_PORT}] Waiting to send TOKEN to {next_port}...")
            time.sleep(0.5)


def run():
    threading.Thread(target=listen, args=(MY_PORT,), daemon=True).start()

    if START_TOKEN:
        time.sleep(2)  # Give time for others to start
        send_token(MY_PORT)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()

# ============coordinator================
import socket
import threading

CS_LOCKED = False

def handle_client(conn):
    global CS_LOCKED
    msg = conn.recv(1024).decode()
    if msg == "REQUEST":
        if not CS_LOCKED:
            conn.send("GRANT".encode())
            CS_LOCKED = True
        else:
            conn.send("DENY".encode())
    elif msg == "RELEASE":
        CS_LOCKED = False
    conn.close()

def run():
    s = socket.socket()
    s.bind(('localhost', 6000))
    s.listen()
    print("[Coordinator] Running...")

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    run()

# ================coordinator_client==============
import socket
import time

PID = 1  # Just a unique identifier for display

def request_cs():
    s = socket.socket()
    s.connect(('localhost', 6000))
    s.send("REQUEST".encode())
    reply = s.recv(1024).decode()
    s.close()
    return reply

def release_cs():
    s = socket.socket()
    s.connect(('localhost', 6000))
    s.send("RELEASE".encode())
    s.close()

def run():
    while True:
        input(f"[{PID}] Press Enter to request CS...")
        reply = request_cs()
        if reply == "GRANT":
            print(f"[{PID}] Entering Critical Section...")
            time.sleep(2)
            print(f"[{PID}] Exiting Critical Section...")
            release_cs()
        else:
            print(f"[{PID}] Access Denied. Try later.")

if __name__ == "__main__":
    run()

# ============== lamport_logical_clock ===============


def lamport_clock():
    n = int(input("Enter number of processes: "))
    clocks = [0] * n
    while True:
        print("\n1. Internal Event\n2. Send Message\n3. Receive Message\n4. Exit")
        ch = int(input("Enter choice: "))
        if ch == 1:
            p = int(input("Enter process number: "))
            clocks[p] += 1
            print(f"Process {p} performed an event, Clock = {clocks}")
        elif ch == 2:
            s = int(input("Enter sender process: "))
            clocks[s] += 1
            print(f"Message sent from P{s} with timestamp {clocks[s]}")
        elif ch == 3:
            r = int(input("Enter receiver process: "))
            t = int(input("Enter received timestamp: "))
            clocks[r] = max(clocks[r], t) + 1
            print(f"Message received by P{r}, Clock = {clocks}")
        elif ch == 4:
            break
        else:
            print("Invalid choice!")


#==============Vector clock====================

def vector_clock():
    n = int(input("Enter number of processes: "))
    VC = [[0 for _ in range(n)] for _ in range(n)]
    while True:
        print("\n1. Internal Event\n2. Send Message\n3. Receive Message\n4. Exit")
        ch = int(input("Enter choice: "))
        if ch == 1:
            p = int(input("Enter process number: "))
            VC[p][p] += 1
            print(f"Internal event in P{p}, VC = {VC[p]}")
        elif ch == 2:
            s = int(input("Enter sender process: "))
            VC[s][s] += 1
            print(f"Message sent from P{s}, VC = {VC[s]}")
        elif ch == 3:
            r = int(input("Enter receiver process: "))
            sv = list(map(int, input("Enter sender vector (space-separated): ").split()))
            for i in range(n):
                VC[r][i] = max(VC[r][i], sv[i])
            VC[r][r] += 1
            print(f"Message received by P{r}, VC = {VC[r]}")
        elif ch == 4:
            break
        else:
            print("Invalid choice!")

print("\n1. Lamport Clock\n2. Vector Clock")
choice = int(input("Enter your choice: "))
if choice == 1:
    lamport_clock()
else:
    vector_clock()