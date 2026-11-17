"""Local concurrency and queue-boundary lesson. No AWS SDK or database service."""

from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from threading import Barrier, Condition, Event, Lock, Semaphore, Thread
import json


def direct_burst(requests=6, database_slots=2):
    """Start all handlers together; hold admitted slots until every attempt is known."""
    if requests < 1 or database_slots < 1:
        raise ValueError("requests and database_slots must be positive")
    start = Barrier(requests)
    slots = Semaphore(database_slots)
    condition = Condition()
    release = Event()
    attempts = 0

    def handle(job_id):
        nonlocal attempts
        start.wait(timeout=5)
        admitted = slots.acquire(blocking=False)
        with condition:
            attempts += 1
            condition.notify_all()
        if admitted:
            try:
                if not release.wait(timeout=5):
                    raise TimeoutError("burst release was not signaled")
            finally:
                slots.release()
        return job_id, "saved" if admitted else "database_busy"

    with ThreadPoolExecutor(max_workers=requests) as executor:
        futures = [executor.submit(handle, job_id) for job_id in range(requests)]
        with condition:
            if not condition.wait_for(lambda: attempts == requests, timeout=5):
                release.set()
                raise TimeoutError("not all handlers attempted the database slot")
        release.set()
        results = dict(future.result(timeout=5) for future in futures)
    return {
        "requests": requests,
        "database_slots": database_slots,
        "saved": sum(value == "saved" for value in results.values()),
        "database_busy": sum(value == "database_busy" for value in results.values()),
        "results": results,
    }


def queued_work(jobs=6, consumers=2, database_slots=2):
    """A volatile local queue lets workers wait for a finite slot instead of rejecting."""
    if min(jobs, consumers, database_slots) < 1:
        raise ValueError("jobs, consumers and database_slots must be positive")
    pending = Queue()
    for job_id in range(jobs):
        pending.put(job_id)
    slots = Semaphore(database_slots)
    observed = []
    record_lock = Lock()
    active = 0
    peak_active = 0
    first_pair = Barrier(2) if jobs >= 2 and consumers >= 2 and database_slots >= 2 else None

    def worker(worker_index):
        nonlocal active, peak_active
        first_job = True
        while True:
            try:
                job_id = pending.get_nowait()
            except Empty:
                return
            try:
                with slots:
                    with record_lock:
                        active += 1
                        peak_active = max(peak_active, active)
                        observed.append(job_id)
                    if first_pair is not None and worker_index < 2 and first_job:
                        first_pair.wait(timeout=5)
                    with record_lock:
                        active -= 1
                    first_job = False
            finally:
                pending.task_done()

    threads = [Thread(target=worker, args=(index,)) for index in range(consumers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    if any(thread.is_alive() for thread in threads):
        raise TimeoutError("local workers did not finish")
    return {
        "submitted": jobs,
        "consumers": consumers,
        "database_slots": database_slots,
        "completed": len(observed),
        "unique_completed": len(set(observed)),
        "peak_database_slots_used": peak_active,
        "remaining": pending.qsize(),
    }


def demonstration():
    direct = direct_burst()
    queued = queued_work()
    return {
        "direct": {key: value for key, value in direct.items() if key != "results"},
        "queued": queued,
        "changed_database_slots": {
            "direct": {key: value for key, value in direct_burst(database_slots=3).items() if key != "results"},
            "queued": queued_work(consumers=3, database_slots=2),
        },
    }


if __name__ == "__main__":
    print(json.dumps(demonstration(), indent=2, sort_keys=True))
