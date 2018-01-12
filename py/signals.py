import json, os, re
from gi.repository import Gtk
from py.song import Song
from py.webbrowser import WebBrowser

class Signals:
	def __init__(self,config):
		self.config = config
	def on_window_destroy(self, window):
		Gtk.main_quit()
	def captcha(self):
		self.config.webbrowser = WebBrowser(self.config,self.config.builder.get_object('webbrowser_scrolledwindow'));
		self.config.builder.get_object('notebook').set_current_page(1)
	def on_webbrowser_changed(self, webview, frame, title):
		if not self.config.webbrowser.isCapchaPage():
			self.on_button2_clicked(False)
	def on_webbrowser_button_clicked(self, widget):
		del self.config.webbrowser
		self.config.builder.get_object('notebook').set_current_page(0)
		self.on_search_button_clicked(False)
	def on_search_button_clicked(self, widget):
		text = self.config.builder.get_object('search_entry').get_text()
		combobox = self.config.builder.get_object('search_combobox')
		index = combobox.get_active()
		model = combobox.get_model()
		self.config.set_config("search_entry",text)
		self.config.set_config("search_combobox",index)
		text = text.replace(' ','+')
		url = 'https://music.yandex.ru/handlers/music-search.jsx?text=' + text + '&type=' + model[index][1] + '&lang=uk'
		raw = self.config.network.go(url,self.config.songs.set_from_json)
	def on_treeview_row_activated(self, treeview, path, view_column):
		self.config.songs.activate(path)
	def on_player_button_clicked(self, widget):
		self.config.player.toggle()
	def on_player_scale_change_value(self, widget, scroll, value):
		self.config.player.go_position(value)
	def on_player_save_button_clicked(self, widget):
		filechooserdialog = Gtk.FileChooserDialog("Save As", self.config.builder.get_object("window"),
			Gtk.FileChooserAction.SAVE,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filechooserdialog.set_current_name(self.config.player.song.get_label() + ".mp3")
		if 'last_folder' in self.config and self.config['last_folder'] is not None:
			filechooserdialog.set_current_folder(self.config['last_folder'])
		#~ self.config.player.pause()
		response = filechooserdialog.run()
		if response != Gtk.ResponseType.OK:
			return False
		filename = filechooserdialog.get_filename()
		if filename == None:
			return None
		if not filename.endswith('.mp3'):
			filename += '.mp3'
		if os.path.exists(str(filename)) == True:
			dialog = Gtk.MessageDialog(filechooserdialog,
				Gtk.DialogFlags.MODAL,
				Gtk.MessageType.QUESTION,
				Gtk.ButtonsType.YES_NO,
				"Replace?")
			response = dialog.run()
			dialog.destroy()
			if response != Gtk.ResponseType.YES:
				return False
		self.config.set_config('last_folder',filechooserdialog.get_current_folder())
		filechooserdialog.destroy()
		if self.config.player.song.save(str(filename)) == True:
			dialog = Gtk.MessageDialog(self.config.builder.get_object("window"),
				Gtk.DialogFlags.MODAL,
				Gtk.MessageType.INFO,
				Gtk.ButtonsType.OK,
				"Song saved to " + str(filename))
			dialog.run()
			dialog.destroy()
		else:
			dialog = Gtk.MessageDialog(self.config.builder.get_object("window"),
				Gtk.DialogFlags.MODAL,
				Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK,
				"Failed to save song")
			dialog.run()
			dialog.destroy()
	def on_menuitem_activate(self, widget):
		widget.run()
	def on_gtk_preferences_activate(self, widget):
		if self.config['proxy'] is not None:
			self.config.builder.get_object("preferences_proxy_entry").set_text(str(self.config['proxy']))
		else:
			self.config.builder.get_object("preferences_proxy_entry").set_text("")
		widget.show()
	def on_dialog_button_clicked(self, widget, test = None):
		widget.hide()
		return True
	#~ def test(self, widget):
		#~ print(widget)
	def on_preferences_button_clicked(self, widget):
		proxy = str(self.config.builder.get_object('preferences_proxy_entry').get_text())
		if re.match("^[A-Za-z0-9\.]*:[0-9]*$",proxy) is not None:
			self.config.set_config("proxy",proxy)
			widget.hide()
		elif proxy == "":
			self.config.set_config("proxy",None)
			widget.hide()
		else:
			dialog = Gtk.MessageDialog(self.config.builder.get_object("window"),
				Gtk.DialogFlags.MODAL,
				Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK,
				"You need to set ip:port or domain:port or leave it empty for proxy")
			dialog.run()
			dialog.destroy()
	def return_true(self,*args):
		return True
	def on_treeview_row_expanded(self,treeview,iter,path):
		index = self.config.songs.model.get_value(iter,0)
		self.config.songs.load_covers(index)
	#~ def on_info_button_clicked(self, widget):
		#~ self.config.builder.get_object('info_dialog').hide()
