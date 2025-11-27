import threading, queue, time, random

NUM_PROCS = 3
ATTEMPTS = 2

# Message queues for each process
queues = [queue.Queue() for _ in range(NUM_PROCS)]
lamport = [0] * NUM_PROCS

def process(pid):
    deferred = []          # list of processes waiting for reply
    requesting = False
    my_request = (None, None)  # (timestamp, pid)

    def send(to, msg):
        queues[to].put((msg, pid, lamport[pid]))

    for i in range(ATTEMPTS):
        time.sleep(random.uniform(0.5, 1.5))

        lamport[pid] += 1
        my_request = (lamport[pid], pid)
        requesting = True
        print(f"[RA] P{pid} requesting CS (ts={my_request[0]})")

        for j in range(NUM_PROCS):
            if j != pid:
                send(j, "REQ")

        replies = 0
        while True:
            msg, sender, t = queues[pid].get()
            lamport[pid] = max(lamport[pid], t) + 1

            if msg == "REQ":
                other_req = (t, sender)
                if requesting and my_request < other_req:
                    deferred.append(sender)
                else:
                    send(sender, "REP")

            elif msg == "REP":
                replies += 1
                if replies == NUM_PROCS - 1:
                    break

        print(f"[RA] P{pid} ENTER CS")
        time.sleep(1)
        print(f"[RA] P{pid} EXIT CS")

        for s in deferred:
            send(s, "REP")
        deferred.clear()
        requesting = False

if __name__ == "__main__":
    for pid in range(NUM_PROCS):
        threading.Thread(target=process, args=(pid,), daemon=True).start()
    time.sleep(20)
