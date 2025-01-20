import queue
import time
import threading
from .actor import Actor


class SchedMgr(Actor):
    """This class provides scheduling service.
    """
    def __init__(self, log_level=0):
        self.name = "sched"
        super().__init__(self.name, log_level=log_level)
        self.sched_items = {}  # Is a dict of scheduled Items.
        self._wake_monitor_thread = None
        self._wake_stop_flag = None
        self._wake_running = False
        self.q_wake = queue.Queue()
        self._run_wake_monitor()

    def _sched_send(self, item_id):
        """ send scheduled item. Check if count completed, remove item.  Otherwise, schedule next launch time."""
        with self.lock:
            sched_item = self.sched_items[item_id]
            task_method = sched_item["task_method"]
            dest_q_name = sched_item["dest_q_name"]
            args = sched_item["args"]
            kwargs = sched_item["kwargs"]
            self.enqueue(dest_q_name, task_method, *args, **kwargs)
            # Update count adn schedule next event
            item_expired = False
            count = sched_item["count"]
            if count > 0:
                next_cnt = count - 1
                if next_cnt <= 0:
                    del self.sched_items[item_id]
                    item_expired = True
                else:
                    self.sched_items[item_id]["count"] = next_cnt
            if not item_expired:
                self.sched_items[item_id]["launch_time"] = sched_item["launch_time"] + sched_item["interval_s"]

    def _check(self):
        items_to_send = []
        # Check items due now
        for item_id, sched_item in self.sched_items.items():
            if sched_item["launch_time"] <= time.time():
                items_to_send.append(item_id)
        # Send due items
        for item_id in items_to_send:
            self._sched_send(item_id)
        # Calculate next wake time
        next_wake = 3
        for sched_item in self.sched_items.values():
            next_wake = min(next_wake, sched_item["launch_time"] - time.time())
        if next_wake < 0:
            next_wake = 0
        # Sched to check at next wake time
        self.q_wake.put(next_wake)  # This will cause the wait monitor to wait the specified time

    ### Methods available for Queue Tasks
    def reset(self, *args, **kwargs):
        # Clear all scheduled items
        self.sched_items = {}
        self._check()

    def del_item(self, source_name: str, sched_id: str):
        # Build the item ID
        item_id = f"{source_name}_{sched_id}"
        # Clear the specified scheduled item
        if item_id in self.sched_items:
            del self.sched_items[item_id]

    def flush_my_items(self, source_name: str):
        # Clear the scheduled items for this caller
        items_to_del = []
        for item_id in self.sched_items.keys():
            # If the itemID begins with the caller name then remove it
            if item_id.startswith(source_name + "_"):
                items_to_del.append(item_id)
        for item_to_del in items_to_del:
            del self.sched_items[item_to_del]

    def schedule(self, source_name, sched_id, interval_s, count, dest_q_name, task_method, *args, **kwargs):
        """
        The scheduler is used to schedule tasks. The tasks will be enqueued at the specified interval.
        """
        item_id = f"{source_name}_{sched_id}"
        launch_time = time.time() + interval_s
        sched_item = {"source": source_name, "name": sched_id, "dest_q_name": dest_q_name, "interval_s": interval_s,
                     "count": count, "launch_time": launch_time,
                     "task_method": task_method, "args": args, "kwargs": kwargs}
        with self.lock:
            self.sched_items.update({item_id: sched_item})
        # Force a check
        self.q_wake.put(0)

    def _run_wake_monitor(self):
        self.log("Task Wake Run Initiated", 5)
        if not self._wake_running:
            self._wake_monitor_thread = threading.Thread(target=self._wake_monitor, args=(), daemon=True)
            self._wake_monitor_thread.start()
        else:
            self.log("Can't run Wake Monitor thread.  It is already running.", 5)

    def _wake_monitor(self):
        """This method waits until next scheduled item is due"""
        self._wake_running = True
        self._wake_stop_flag = False
        next_wake = 3
        while not self._wake_stop_flag:
            try:
                next_wake_time = self.q_wake.get(timeout=next_wake)
            except queue.Empty:
                next_wake = 3  # Set default next wake.  Will be changed by Check
                self._check()  # Check will enqueue next wait time
            else:
                if next_wake_time is None:
                    # Exiting.  End thread.
                    self._wake_stop_flag = True
                else:
                    next_wake = next_wake_time
        self._wake_running = False

    def stop(self):
        self._wake_stop_flag = True
        if self._wake_running:
            try:
                self.q_wake.put(None)
                self._wake_monitor_thread.join()
            except:
                pass
        super().stop()
