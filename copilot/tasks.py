import threading
import queue

class TaskProcessor:
    def __init__(self, num_workers=4):
        self.task_queue = queue.Queue()
        self.workers = []
        self._init_workers(num_workers)

    def _init_workers(self, num_workers):
        for _ in range(num_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker(self):
        while True:
            task = self.task_queue.get()
            if task is None:  # Stop signal
                break
            try:
                task()  # Execute the task
            except Exception as e:
                print(f"Error processing task: {e}")
            finally:
                self.task_queue.task_done()

    def add_task(self, task):
        self.task_queue.put(task)

    def stop(self):
        # Add stop signals for each worker
        for _ in self.workers:
            self.task_queue.put(None)
        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()


