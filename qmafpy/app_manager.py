from .globals import App
from .log_manager import AppLogger
from .config_manager import CfgMgr
from .subscription import SubsriptionMgr
from .scheduler import SchedMgr

class AppMgr:
    #### Configuration Methods ####
    @staticmethod
    def init_config(working_dir):  # Can skip this method and use different log manager
        App.cfg_mgr = CfgMgr(working_dir)
        App.cfg_mgr.init_working_dirs()
        App.cfg = App.cfg_mgr.get_cfg()

    #### Logging Methods ####
    @staticmethod
    def init_logger():  # Can skip this method and use different log manager
        App.logger = AppLogger(App.cfg["logs_dir"], App.cfg["app_name"])
        App.logger.log("App Launch")

    ### Sched and Subscription
    @staticmethod
    def init_services():  # Can skip this method and use different log manager
        App.subs_mgr = SubsriptionMgr()
        App.scheduler = SchedMgr()

