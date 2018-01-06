import json, os, re
from gi.repository import Gtk, Gio, GdkPixbuf
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
		text = self.config.builder.get_object('search_entry').get_text().replace(' ','+')
		combobox = self.config.builder.get_object('search_combobox')
		index = combobox.get_active()
		model = combobox.get_model()
		url = 'https://music.yandex.ru/handlers/music-search.jsx?text=' + text + '&type=' + model[index][1] + '&lang=uk'
		raw = self.config.network.go(url,self.on_search_received)
	def on_search_received(self,raw):
		if raw == False:
			return False
		if ('<!DOCTYPE html>' == raw[0:15]):
			self.captcha()
		else:
			self.parse_resp(json.loads(raw))
	def parse_resp(self, data):
		ts = self.config.builder.get_object('treestore')
		ts.clear()
		for i in data['artists']['items']:
			big_cover_url = None
			if 'cover' in i:
				url = 'https://'+i['cover']['uri'].replace('%%','50x50')
				big_cover_url = 'https://' + i['cover']['uri'].replace('%%','400x400')
			pi = ts.append(None,[i['id'],None,None,None,i['name'],'','',None,'',big_cover_url])
			if 'cover' in i:
				self.config.network.go(url,self.load_cover,url,ts,pi)
			for j in i['popularTracks']:
				durs = j['durationMs']/1000
				big_cover_url = None
				if 'coverUri' in j['albums'][0]:
					url = 'https://' + j['albums'][0]['coverUri'].replace('%%','50x50')
					big_cover_url = 'https://' + j['albums'][0]['coverUri'].replace('%%','400x400')
				pti = ts.append(pi,[
					i['id'],
					j['albums'][0]['id'],
					j['id'],
					None,
					i['name'],
					j['albums'][0]['title'],
					j['title'],
					durs,
					str(durs/60) + ':' + str(durs/10%6)+str(durs%10),
					big_cover_url
				])
				if 'coverUri' in j['albums'][0]:
					self.config.network.go(url,self.load_cover,url,ts,pti)
		for j in data['tracks']['items']:
			durs = j['durationMs']/1000
			big_cover_url = None
			if 'coverUri' in j['albums'][0]:
				url = 'https://' + j['albums'][0]['coverUri'].replace('%%','50x50')
				big_cover_url = 'https://' + j['albums'][0]['coverUri'].replace('%%','400x400')
			pti = ts.append(None,[
				j['artists'][0]['id'],
				j['albums'][0]['id'],
				j['id'],
				None,
				j['artists'][0]['name'],
				j['albums'][0]['title'],
				j['title'],
				durs,
				str(durs/60) + ':' + str(durs/10%6)+str(durs%10),
				big_cover_url
			])
			if 'coverUri' in j['albums'][0]:
				self.config.network.go(url,self.load_cover,url,ts,pti)
	def load_cover(self,raw,url,model,iter,count=0):
		if raw == False:
			if count < 10:
				self.config.network.go(self,raw,url,model,iter,count+1)
			return False
		input_stream = Gio.MemoryInputStream.new_from_data(raw, None)
		pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
		model.set(iter,3,pixbuf)
	def on_treeview_row_activated(self, treeview, path, view_column):
		ts = self.config.builder.get_object('treestore')
		ti = ts.get_iter(path)
		data = {
			'albumid': ts.get_value(ti,1),
			'trackid': ts.get_value(ti,2),
			'cover': ts.get_value(ti,3),
			'artist': ts.get_value(ti,4),
			'album': ts.get_value(ti,5),
			'track': ts.get_value(ti,6),
			'duration': ts.get_value(ti,7),
			'bigcover': ts.get_value(ti,9),
			'config': self.config,
		}
		if (data['albumid'] and data['trackid']):
			self.config.player.play(Song(**data))
	def on_player_button_clicked(self, widget):
		self.config.player.toggle()
	def on_player_scale_change_value(self, widget, scroll, value):
		self.config.player.go_position(value)
	def on_player_save_button_clicked(self, widget):
		filechooserdialog = self.config.builder.get_object('song_filechooserdialog')
		filechooserdialog.set_current_name(self.config.player.song.get_label() + ".mp3")
		self.config.player.pause()
		filechooserdialog.show()
	def on_song_activated(self, widget):
		filechooserdialog = self.config.builder.get_object('song_filechooserdialog')
		filename = filechooserdialog.get_filename()
		if filename == None:
			return None
		if not filename.endswith('.mp3'):
			filename += '.mp3'
		if os.path.exists(str(filename)) == True:
			dialog = Gtk.MessageDialog(self.config.builder.get_object("window"),
				Gtk.DialogFlags.MODAL,
				Gtk.MessageType.QUESTION,
				Gtk.ButtonsType.YES_NO,
				"Replace?")
			response = dialog.run()
			dialog.destroy()
			if response == Gtk.ResponseType.NO:
				return False
		filechooserdialog.hide()
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
		widget.show()
	def on_gtk_preferences_activate(self, widget):
		for i in self.config:
			if self.config[i] is not None:
				self.config.builder.get_object("preferences_"+i+"_entry").set_text(str(self.config[i]))
			else:
				self.config.builder.get_object("preferences_"+i+"_entry").set_text("")
		widget.show()
	def on_dialog_button_clicked(self, widget, test = None):
		widget.hide()
	#~ def test(self, widget):
		#~ print(widget)
	def on_preferences_button_clicked(self, widget):
		proxy = str(self.config.builder.get_object('preferences_proxy_entry').get_text())
		if re.match("^[A-Za-z0-9.]*:[0-9]*$",proxy) is not None:
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
	#~ def on_info_button_clicked(self, widget):
		#~ self.config.builder.get_object('info_dialog').hide()
