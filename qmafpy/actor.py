import threading
import queue
from .globals import App


class Actor:
    """This is a generic class meant to be inherited when building specific modules.
        At initialization:
            Create a local queue
            Store its queue to the global QList class.
        When run method is called it launches an autonomous thread the dequeues task items.
            Dequeued items will call a method to process them.
        When the 'exit' task is received, the dequeue loop will close.
    """

    #### Initialize
    def __init__(self, name: str, log_level=0, auto_start=True):
        self.name = name
        self.log_level = log_level
        self.cfg = App.cfg
        self.q = App.create_queue(self.name)
        self._running = False
        self.received_data = {}
        self._stop_flag = False
        self.task_monitor_thread = None
        self.lock = threading.RLock()
        self.callable_task_list = [
            attr for attr in dir(self)
            if callable(getattr(self, attr)) and not attr.startswith("_")
            ]
        if auto_start:
            self.run()

    #### Default methods of queued state machines
    def set_log_level(self, level: int):
        """Update the verbose level of logging event messages for this module."""
        self.log_level = level

    def log(self, msg, level=0):
        """This method writes messages to the command window and also to a log file"""
        if level <= self.log_level:
            # Log to File
            if hasattr(App, 'logger') and App.logger is not None:
                App.logger.log(f"{self.name} {msg}")
            else:
                # Write to cmd window
                print(self.name + " " + msg)

    ### Subscriptions
    def subscribe(self, topic: str, callback_method, attributes=None, subs_id=None):
        """This method will subscribe to data"""

        if hasattr(App, 'subs_mgr'):
            self.log(f"Subscribe topic={topic} dest_q={self.name} task_method={callback_method}", 5)
            App.subs_mgr.add_subscription(topic, self.name, callback_method, attributes=attributes, subs_id=subs_id)

    def publish(self, topic: str, data):
        """This method will publish data"""
        if hasattr(App, 'subs_mgr'):
            self.log("published topic " + topic, 5)
            App.subs_mgr._publish(topic, data)

    def run(self):
        """This method launches the dequeue loop in an autonomous thread"""
        self.log("Task Monitor Run Initiated", 5)
        if not self._running:
            self.task_monitor_thread = threading.Thread(target=self._task_queue_thread, args=(), daemon=True)
            self.task_monitor_thread.start()
        else:
            self.log("Can't run Task Monitor thread.  It is already running.", 5)

    def _task_queue_thread(self):
        """This method loops processing enqueued tasks"""
        self.log("Task Monitor Running", 5)
        self._running = True
        self._stop_flag = False
        while not self._stop_flag:
            task_data = self.q.get()
            if task_data is None:
                self._stop_flag = True
            else:
                is_error = False
                task, args, kwargs = task_data
                self.log(f"Dequeue task={task}, args={args}, kwargs={kwargs}", 5)
                task_method = task
                if type(task) == str:
                    if task in self.callable_task_list:
                        task_method = getattr(self, task)
                    else:
                        is_error = True
                        self.log(f"ERROR: Dequeued invalid task: {task}")
                if not is_error:
                    try:
                        task_method(*args, **kwargs)
                    except Exception as e:
                        self.log(f"ERROR: Exception performing task {task_data}: {e}")
            self.q.task_done()
        self._running = False

    def flush_received_data(self, topic=None):
        if topic is None: # FLush all data
            self.received_data = {}
        else: # Flush only topic
            if topic in self.received_data:
                del self.received_data[topic]

    def receive_data(self, topic, data):
        self.log(f"Receive Data topic={topic}, data={data}", 5)
        self.received_data[topic] = data

    def enqueue_local(self,task_method, *args, **kwargs):
        self.q.put((task_method, args, kwargs))

    def send_data(self, q_name, topic, data):
        self.log(f"Send Data dest={q_name}, topic={topic}, data={data}" , 5)
        dest_q = App.get_queue(q_name)
        if dest_q is not None:
            dest_q.put(("data_input", (topic,data), {}))
        else:
            self.log(f"ERROR: dest_q does not exist.  Send Data dest={q_name}", 0)

    def enqueue(self,q_name, task_method, *args, **kwargs):
        self.log(f"Enqueue dest={q_name} task={task_method} args={args}", 5)
        dest_q = App.get_queue(q_name)
        if dest_q is not None:
            dest_q.put((task_method, args, kwargs))
        else:
            self.log(f"ERROR: dest_q does not exist.  Enqueue dest={q_name} task={task_method} args={args}", 0)

    def task_query(self, q_name, task_method, timeout, *args, **kwargs):
        data = None
        rtn_code = 0
        self.log(f"Query dest={q_name} task={task_method} args={args}", 5)
        dest_q = App.get_queue(q_name)
        if dest_q is not None:
            rtn_q = queue.Queue()
            kwargs.update({"return_q":rtn_q})
            dest_q.put((task_method, args, kwargs))
            try:
                rtn_q.get(timeout=timeout)
            except queue.Empty:
                self.log(f"ERROR: Query timeout. Dest={q_name} task={task_method} args={args}", 0)
                rtn_code = -1
        else:
            rtn_code = -1
            self.log(f"ERROR: dest_q does not exist.  Query dest={q_name} task={task_method} args={args}", 0)
        return rtn_code, data

    def sched_local(self,sched_id, interval_s, count, task_method, *args, **kwargs):
        App.scheduler.schedule(self.name, sched_id, interval_s, count, self.name, task_method, *args, **kwargs)

    def sched(self,sched_id, interval_s, count, dest_q_name, task_method, *args, **kwargs):
        self.log(f"Schedule Event sched_id={sched_id}, interval={interval_s}, cnt={count}, dest_q={dest_q_name}, task_method={task_method}", 5)
        App.scheduler.schedule(self.name, sched_id, interval_s, count, dest_q_name, task_method, *args, **kwargs)

    def sched_del_item(self,sched_id):
        self.log(f"Schedule Cancel Event sched_id={sched_id}", 5)
        App.scheduler.del_item(self.name, sched_id)

    def stop(self):
        self._stop_flag = True
        if self._running:
            try:
                self.q.put(None)
                self.task_monitor_thread.join()
            except:
                pass

    def reset(self, *args, **kwargs):
        """This method resets is actor
        Override this method with logic to handle other items that need to be reset."""
        # Flush any scheduled tasks
        App.scheduler.flush_my_items(self.name)
        # Empty queue
        while not self.q.empty():
            self.q.get()

    def exit(self, *args, **kwargs):
        """Exit this actor - close the running dequeue thread"""
        self.log("Exiting", 1)
        self.stop()
        self.log("Exited", 1)

