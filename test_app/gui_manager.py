import tkinter as tk
from tkinter import ttk
from catspy import Actor


class GuiMgr(Actor):
    def __init__(self, root, log_level=0):
        self.name = "gui"
        self.root = root
        self.indicators = {}
        self.buttons = {}
        self.subframes = {}
        self.bg1 = "navajowhite2"
        self.bg2 = "steelblue1"
        super().__init__(self.name, log_level=log_level)
        self.root.geometry = "600x400"
        self.root.title(self.cfg["app_name"])
        fr1=tk.Frame(self.root, bg=self.bg1, width=200)
        fr1.pack(side=tk.LEFT, fill=tk.Y)
        fr2 = tk.Frame(self.root, bg=self.bg2, width=400)
        fr2.pack(side=tk.LEFT, fill=tk.Y)
        font_10_bold = ("Arial", 10, "bold")
        bg_indicator= "Light Grey"

        row_sel = 0
        tk.Button(fr1, text="Read A", font=font_10_bold, width=20,
                  command=lambda: self.enqueue("te", "read_1")).grid(row=row_sel, padx=4, pady=8,
                                                                     sticky=tk.W)

        row_sel += 1
        tk.Button(fr1, text="Read B", font=font_10_bold, width=20,
                  command=lambda: self.enqueue("te", "read_2")).grid(row=row_sel, padx=4, pady=8,
                                                                     sticky=tk.W)
        row_sel += 1
        tk.Button(fr1, text="Read C", font=font_10_bold, width=20,
                  command=lambda: self.enqueue("te", "read_3")).grid(row=row_sel, padx=4, pady=8,
                                                                         sticky=tk.W)
        row_sel += 1
        tk.Button(fr1, text="Read All (Publish)", font=font_10_bold, width=20,
                  command=lambda: self.enqueue("te", "read_all")).grid(row=row_sel, padx=4, pady=8,
                                                                       sticky=tk.W)
        row_sel += 1
        tk.Button(fr1, text="Sched Single", font=font_10_bold, width=20,
                  command=lambda: self.sched("Read_Device", 1, 1, "te",
                                             "read_all")).grid(row=row_sel, padx=4, pady=8, sticky=tk.W)
        row_sel += 1
        tk.Button(fr1, text="Sched Continuous", font=font_10_bold, width=20,
                  command=lambda: self.sched("Read_Device", 1, 0, "te",
                                             "read_all")).grid(row=row_sel, padx=4, pady=8,sticky=tk.W)
        row_sel += 1
        tk.Button(fr1, text="Sched Stop", font=font_10_bold, width=20,
                  command=lambda: self.sched_del_item("Read_Device")).grid(row=row_sel, padx=4, pady=8, sticky=tk.W)


        indicators = [ # (Caption, Indicator_name, Subscription_topic)
            ("Data A", "data_1", "DATA_1"),
            ("Data B", "data_2", "DATA_2"),
            ("Data C", "data_3", "DATA_3"),
        ]
        row_sel = -1

        for caption, name, subs_topic in indicators:
            row_sel += 1
            self.subframes[caption] = tk.Frame(fr2, bg=self.bg2)
            self.subframes[caption].grid(row=row_sel, pady=4, padx=4, sticky=tk.EW)
            tk.Label(self.subframes[caption], text=caption, font=font_10_bold, bg=self.bg2).pack(side=tk.LEFT)
            self.indicators[name] = tk.StringVar()
            tk.Label(self.subframes[caption], width=20, font=font_10_bold, textvariable = self.indicators[name],
                     bg=bg_indicator, relief=tk.SUNKEN).pack(side=tk.RIGHT)
            self.subscribe(subs_topic, self.receive_published_data, {"indicator":name})

        indicators = [  # (Caption, Indicator_name, Subscription_topic)
            ("Data A2", "data_1a", "DATA_1"),
            ("Data B2", "data_2a", "DATA_2"),
            ("Data C2", "data_3a", "DATA_3"),
        ]
        for caption, name, subs_topic in indicators:
            row_sel += 1
            self.subframes[caption] = tk.Frame(fr2, bg=self.bg2)
            self.subframes[caption].grid(row=row_sel, pady=4, padx=4, sticky=tk.EW)
            tk.Label(self.subframes[caption], text=caption, font=font_10_bold, bg=self.bg2).pack(side=tk.LEFT)
            self.indicators[name] = tk.StringVar()
            tk.Label(self.subframes[caption], width=20, font=font_10_bold, textvariable=self.indicators[name],
                     bg=bg_indicator, relief=tk.SUNKEN).pack(side=tk.RIGHT)
            self.subscribe(subs_topic, self.receive_published_data, {"indicator": name})

    def receive_published_data(self, topic, attributes, value):
        if attributes is not None and "indicator" in attributes:
            indicator_name = attributes["indicator"]
            self.indicators[indicator_name].set(f"{value}")

    def set_indicator(self, name, value):
        self.indicators[name].set(f"{value}")






