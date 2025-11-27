import threading, time, random

NUM_PROCS = 3
ATTEMPTS = 2

class TokenRing:
    def __init__(self, n):
        self.token = 0
        self.lock = threading.Lock()
        self.n = n

    def pass_token(self):
        with self.lock:
            self.token = (self.token + 1) % self.n

ring = TokenRing(NUM_PROCS)

def process(pid):
    for i in range(ATTEMPTS):
        time.sleep(random.uniform(0.5, 1.5))
        while ring.token != pid:
            time.sleep(0.1)
        print(f"[TokenRing] P{pid} ENTER CS")
        time.sleep(1)
        print(f"[TokenRing] P{pid} EXIT CS")
        ring.pass_token()

if __name__ == "__main__":
    for pid in range(NUM_PROCS):
        threading.Thread(target=process, args=(pid,), daemon=True).start()
    time.sleep(10)
