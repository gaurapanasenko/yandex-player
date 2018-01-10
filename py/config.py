import os, tempfile, getpass, json
from py.network import Network

class Config():
	def __init__(self):
		self.ui_file = os.path.dirname(os.path.realpath(__file__)) + "/../ui/yandex_player.ui"
		self.data = {"proxy" : None, "last_folder" : None}
		self.config_folder = os.path.expanduser("~") + "/.config/yandex-player"
		self.temp_folder = tempfile.gettempdir() + "/yandex-player-" + getpass.getuser()
		self.cookies_file = self.config_folder + "/cookies.txt"
		self.config_file = self.config_folder + "/config.json"
		if os.path.exists(self.config_file):
			with open(self.config_file, 'r') as f:
				self.data.update(json.load(f))
	def set_config(self,key,value):
		self.data[key] = value
		if (key == "proxy"):
			del self.network
			self.network = Network(self)
		with open(self.config_file, 'w+') as f:
			json.dump(self.data, f)
	def __getitem__(self, index):
		return self.data[index]
	def __iter__(self):
		return (i for i in self.data)
