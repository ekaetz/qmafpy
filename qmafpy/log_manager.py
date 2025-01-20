import os
from datetime import datetime

class AppLogger():
	"""This module handles logging of app status messages.
	"""
	def __init__(self, log_dir, app_name):
		self.log_dir = log_dir
		self.app_name = app_name
		self.log_file_date = None
		self.log_file = None

	def log(self, msg):
		"""Add time stamp then write to log file.
		"""
		log_msg = str(datetime.now())[:-3] + ": " + msg
		self._logMessage(log_msg)

	def open_new_file(self):
		if self.log_file is not None:
			try:
				self.log_file.close()
			except:
				pass
		self.log_file_date = datetime.now().strftime("%Y%m%d")
		file_name = "Log_" + self.app_name + "_" + self.log_file_date + ".txt"
		file_path = os.path.join(self.log_dir, file_name)
		self.log_file = open(file_path, 'a')

	def _logMessage(self, msg: str):
		"""Write to log file.
		"""
		if self.log_file is None or self.log_file_date != datetime.now().strftime("%Y%m%d"):
			self.open_new_file()
		# 1) Print to StdOut
		print(msg)
		# 2) Write to log file
		self.log_file.write(msg + "\n")
		self.log_file.flush()

	def close(self):
		if self.log_file != None:
			try:
				self.log_file.close()
				self.log_file = None
			except:
				pass

	def exit(self):
		self.close()
