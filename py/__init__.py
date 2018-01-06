import os
from gi.repository import GObject, Gtk
from py.config import Config
from py.signals import Signals
from py.spinner import Spinner
from py.network import Network
from py.player import Player

def main():
	GObject.threads_init()
	config = Config()
	if os.path.exists(config.config_folder) == False:
		os.makedirs(config.config_folder)
	if os.path.exists(config.temp_folder) == False:
		os.makedirs(config.temp_folder)
	config.signals = Signals(config)
	config.builder = Gtk.Builder()
	config.builder.add_from_file(config.ui_file)
	config.builder.connect_signals(config.signals)
	config.spinner = Spinner(config.builder.get_object('spinner'))
	config.network = Network(config)
	config.player = Player(
			config.builder.get_object('player_grid'),
			config.builder.get_object('player_image'),
			config.builder.get_object('player_button_image'),
			config.builder.get_object('player_label'),
			config.builder.get_object('player_adjustment'))
	#~ config.builder.get_object('window').show_all()
	#~ config.signals.captcha()
	Gtk.main()
