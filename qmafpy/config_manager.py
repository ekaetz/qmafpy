import os
import sys
import json


class CfgMgr:
    def __init__(self, working_dir=None):
        self.working_dir = working_dir
        self.cfg = {}
        self.cwd = os.getcwd()
        import __main__
        self.app_dir = self.cwd
        if hasattr(__main__, "__file__"):
            self.app_dir = os.path.dirname(os.path.abspath(__main__.__file__))
        if self.working_dir is None:
            self.working_dir = self.app_dir
        self.is_exe = getattr(sys, 'frozen', False)
        if self.is_exe:
            app_root_dir = sys._MEIPASS
        else:
            app_root_dir = self.app_dir
        self.cfg["working_dir"] = self.working_dir
        self.cfg["cwd"] = self.cwd
        self.cfg["is_exe"] = self.is_exe
        self.cfg["app_dir"] = self.app_dir
        self.cfg["app_root_dir"] = app_root_dir   # Used for accessing items bundled in the executable.
        config_path = os.path.join(self.app_dir, "app_config.json")
        if os.path.exists(config_path):
            self.load_cfg_from_file(config_path)

    def init_working_dirs(self):
        """
        1) Add working folders to the config if not in config
            config_dir = <working_dir>/config
            logs_dir = <working_dir>/logs
            results_dir = <working_dir>/results
            sequences_dir = <working_dir>/sequences
        2) Create working folders if they do not exist.
        3) Check for app_config.json in the config folder
            If it exists, merge the configuration
        """
        name_dir_list = {
            "logs_dir":"logs",
            "config_dir": "config",
            "results_dir": "results",
            "sequences_dir": "sequences"
        }
        for key, value in name_dir_list.items():
            folder_path = os.path.join(self.working_dir, value)
            self.cfg[key] = folder_path
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        config_path = os.path.join(self.cfg["config_dir"], "app_config.json")
        if os.path.exists(config_path):
            self.load_cfg_from_file(config_path)

    def get_cfg(self):
        return self.cfg

    def print_config(self):  # Used for debugging
        print("Configuration:")
        for key, value in self.cfg.items():
            print(f"    {key}={value}")

    def load_cfg_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                new_cfg = json.load(f)
            self.cfg.update(new_cfg)
        except Exception as e:
            print(f"ERROR loading config file 'file_path': {e}")




