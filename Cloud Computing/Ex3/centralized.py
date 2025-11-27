import threading, queue, time, random

NUM_PROCS = 3
ATTEMPTS = 2

coordinator = queue.Queue()
grant_queues = [queue.Queue() for _ in range(NUM_PROCS)]

def coordinator_process():
    cs_busy = False
    # waiting = []

    while True:
        if not cs_busy and not coordinator.empty():
            pid = coordinator.get()
            grant_queues[pid].put("GRANT")
            cs_busy = True
        else:
            # check if someone has exited
            for pid in range(NUM_PROCS):
                try:
                    msg = grant_queues[pid].get_nowait()
                    if msg == "RELEASE":
                        cs_busy = False
                except:
                    pass
        time.sleep(0.1)


def process(pid):
    for i in range(ATTEMPTS):
        time.sleep(random.uniform(0.5, 1.5))
        print(f"[Centralized] P{pid} requesting CS")
        coordinator.put(pid)
        grant_queues[pid].get()   # wait for GRANT
        print(f"[Centralized] P{pid} ENTER CS")
        time.sleep(1)
        print(f"[Centralized] P{pid} EXIT CS")
        grant_queues[pid].put("RELEASE")

if __name__ == "__main__":
    threading.Thread(target=coordinator_process, daemon=True).start()
    for pid in range(NUM_PROCS):
        threading.Thread(target=process, args=(pid,), daemon=True).start()
    time.sleep(10)
