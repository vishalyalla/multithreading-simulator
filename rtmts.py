import streamlit as st
import threading
import time
import random
import matplotlib.pyplot as plt
from threading import Semaphore, Lock, Condition
from queue import Queue

# ---------------- THREAD CLASS ----------------
class SimulatedThread:
    def __init__(self, tid):
        self.tid = tid
        self.state = "NEW"
        self.arrival = 0
        self.burst = random.randint(1, 3)
        self.start = 0
        self.finish = 0

    def run(self, log, current_time):
        self.state = "RUNNING"
        self.start = current_time
        log.append((self.tid, current_time, self.burst))
        time.sleep(self.burst * 0.5)
        self.state = "TERMINATED"
        self.finish = self.start + self.burst

# ---------------- SCHEDULING ----------------
def fcfs(threads):
    time_now = 0
    log = []

    for t in threads:
        t.run(log, time_now)
        time_now += t.burst

    return log


def round_robin(threads, quantum=1):
    queue = threads[:]
    time_now = 0
    log = []

    while queue:
        t = queue.pop(0)
        t.state = "RUNNING"

        run_time = min(quantum, t.burst)
        log.append((t.tid, time_now, run_time))

        time.sleep(run_time * 0.5)
        t.burst -= run_time
        time_now += run_time

        if t.burst > 0:
            t.state = "READY"
            queue.append(t)
        else:
            t.state = "TERMINATED"

    return log

# ---------------- GANTT CHART ----------------
def gantt_chart(log):
    fig, ax = plt.subplots()

    for tid, start, duration in log:
        ax.barh(str(tid), duration, left=start)

    ax.set_xlabel("Time")
    ax.set_ylabel("Threads")
    ax.set_title("Gantt Chart")
    st.pyplot(fig)

# ---------------- SEMAPHORE ----------------
sem = Semaphore(2)

def semaphore_task(tid, output):
    output.append(f"Thread {tid} waiting")
    sem.acquire()

    output.append(f"Thread {tid} in critical section")
    time.sleep(1)

    output.append(f"Thread {tid} leaving")
    sem.release()

# ---------------- MONITOR ----------------
class Monitor:
    def __init__(self):
        self.lock = Lock()
        self.cond = Condition(self.lock)
        self.data = 0

    def produce(self, output):
        with self.lock:
            self.data += 1
            output.append(f"Produced {self.data}")
            self.cond.notify()

    def consume(self, output):
        with self.cond:
            while self.data == 0:
                self.cond.wait()

            output.append(f"Consumed {self.data}")
            self.data -= 1

# ---------------- DEADLOCK SIM ----------------
def deadlock_demo():
    return [
        "Thread 1 waiting for Resource 2",
        "Thread 2 waiting for Resource 1",
        "Deadlock Occurred!"
    ]

# ---------------- UI ----------------
st.title("🧠 Multithreading Simulator")

model = st.selectbox("Thread Model", ["Many-to-One", "One-to-One", "Many-to-Many"])
algo = st.selectbox("Scheduling Algorithm", ["FCFS", "Round Robin"])
num_threads = st.slider("Number of Threads", 2, 10, 5)

# ---------------- RUN SIMULATION ----------------
if st.button("Run Simulation"):

    threads = [SimulatedThread(i) for i in range(num_threads)]

    st.subheader("Thread Execution")

    # Model Simulation
    if model == "Many-to-One":
        st.write("⚠ Only one thread runs at a time")
        log = fcfs(threads)

    elif model == "One-to-One":
        st.write("⚡ Parallel execution")
        ths = []
        log = []

        for t in threads:
            th = threading.Thread(target=t.run, args=(log, 0))
            ths.append(th)
            th.start()

        for th in ths:
            th.join()

    else:
        st.write("🔀 Limited parallelism")
        log = []
        for i in range(0, len(threads), 2):
            batch = threads[i:i+2]
            for t in batch:
                t.run(log, i)

    # Scheduling
    if algo == "Round Robin":
        log = round_robin(threads)

    # Display states
    st.subheader("Thread States")
    for t in threads:
        st.write(f"Thread {t.tid} → {t.state}")

    # Gantt chart
    st.subheader("Gantt Chart")
    gantt_chart(log)

# ---------------- SEMAPHORE DEMO ----------------
if st.button("Run Semaphore Demo"):
    output = []
    ths = []

    for i in range(4):
        t = threading.Thread(target=semaphore_task, args=(i, output))
        ths.append(t)
        t.start()

    for t in ths:
        t.join()

    st.subheader("Semaphore Output")
    for line in output:
        st.write(line)

# ---------------- MONITOR DEMO ----------------
if st.button("Run Monitor (Producer-Consumer)"):
    monitor = Monitor()
    output = []

    p = threading.Thread(target=monitor.produce, args=(output,))
    c = threading.Thread(target=monitor.consume, args=(output,))

    p.start()
    c.start()

    p.join()
    c.join()

    st.subheader("Monitor Output")
    for line in output:
        st.write(line)

# ---------------- DEADLOCK ----------------
if st.button("Show Deadlock"):
    st.subheader("Deadlock Simulation")
    for line in deadlock_demo():
        st.write(line)

# ---------------- METRICS ----------------
st.subheader("Performance Metrics (Sample)")
st.metric("Throughput", f"{num_threads}/sec")
st.metric("Avg Waiting Time", f"{round(random.uniform(1,3),2)} sec")
st.metric("CPU Utilization", f"{random.randint(60,95)} %")