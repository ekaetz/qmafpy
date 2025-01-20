from catspy import Actor
import time
import random

class TestExec(Actor):
    def __init__(self, log_level=0):
        super().__init__("te", log_level=log_level)

    def read_1(self):
        time.sleep(0.1)
        data = round(10 + random.random() * 2,3)
        self.gui_update("data_1", data)

    def read_2(self):
        data = round(20 + random.random() * 2, 3)
        self.gui_update("data_2", data)

    def read_3(self):
        data = round(30 + random.random() * 2, 3)
        self.gui_update("data_3", data)

    def read_all(self):
        time.sleep(0.1)
        data1 = round(10 + random.random() * 2, 3)
        data2 = round(20 + random.random() * 2, 3)
        data3 = round(30 + random.random() * 2, 3)
        self.publish("DATA_1", data1)
        self.publish("DATA_2", data2)
        self.publish("DATA_3", data3)

    def gui_update(self, name, value):
        self.enqueue("gui", "set_indicator", name, value)
