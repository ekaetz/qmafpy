import queue
import threading
import time


class BorgMeta(type):
  """
  This metaclass is used to convert a class into a Borg class.
  Borg classes have all of their instances share the same internal
  state dictionary.
  Usage: when creating a borg class, just include: 'metaclass=BorgMeta'
    in the class declaration's parenthesis. Ex. `class NewBorg(object, metaclass=BorgMeta)`
  """
  def __init__(cls, cls_name, parents, dct):
    type.__init__(cls, cls_name, parents, dct)

    # Do some monkey-wrenching.
    old_init = cls.__init__
    cls._borg_state = None

    def new_init(self, *args, **kwargs):
      if cls._borg_state is None:
        cls._borg_state = self.__dict__
        old_init(self, *args, **kwargs)
      else:
        self.__dict__ = cls._borg_state

    cls.__init__ = new_init


class App(object, metaclass=BorgMeta):
    """
    This is a borg class.  The same instance is provided each time a module instantiates it.
    This makes it global to all modules in the application.
    """
    # Initial Class Properties (More can be added by other modules)
    cfg = {}
    data = {}  # Shared Data
    queues = {}
    log_levels = {}
    cfg_mgr = None
    logger = None
    subs_mgr = None
    scheduler = None
    lock = threading.RLock()

    @staticmethod
    def set_log_level(name, level):
        App.log_levels[name] = level

    @staticmethod
    def log(msg):
        print(msg)
        if App.logger is not None:
            App.logger.log_msg(msg)

    #### Queue Methods ####
    @staticmethod
    def add_queue(name, q_ref):
        with App.lock:
            App.queues[name] = q_ref

    @staticmethod
    def create_queue(name):
        q_ref = queue.Queue()
        with App.lock:
            App.queues[name] = q_ref
        return q_ref

    @staticmethod
    def get_queue(name):
        return App.queues.get(name, None)

    @staticmethod
    def update_log_levels(log_levels:dict):
        for name, level in log_levels.items():
            dest_q = App.queues.get(name, None)
            if dest_q is not None:
                dest_q.put(("set_log_level", (level,),{}))

    @staticmethod
    def exit():
        for dest_q in App.queues.values():
            dest_q.put(("exit", (), {}))
        time.sleep(0.1)






