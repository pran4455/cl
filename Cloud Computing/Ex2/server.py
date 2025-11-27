import Pyro4

@Pyro4.expose
class Calculator:
    def add_numbers(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

def main():
    daemon = Pyro4.Daemon()  # Start Pyro daemon
    uri = daemon.register(Calculator)  # Register Calculator object
    print("Calculator service is running.")
    print("URI:", uri)  # Share this URI with client
    daemon.requestLoop()  # Wait for calls

if __name__ == "__main__":
    main()
