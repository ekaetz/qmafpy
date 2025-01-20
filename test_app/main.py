from catspy import App, AppMgr
import tkinter as tk
from test_app.gui_manager import GuiMgr
from test_app.test_exec import TestExec


AppMgr.init_config(r"C:\CATS")
App.cfg["app_name"] = "Test_Executive"
App.cfg["app_version"] = "Beta_1.0"
AppMgr.init_logger()
AppMgr.init_services()
root = tk.Tk()
App.gui = GuiMgr(root)
App.te = TestExec()
log_levels = {"gui":0, "te":0}
App.update_log_levels(log_levels)
root.mainloop()
App.exit()



