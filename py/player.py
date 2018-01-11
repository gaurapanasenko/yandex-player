import pygame, threading, time
from gi.repository import Gtk, GLib
from py.song import Song
import time

class Player:
	def __init__(self,grid,cover_obj,button_img,label,adjustment):
		pygame.mixer.init()
		self.position = 0
		self.grid = grid
		self.cover_obj = cover_obj
		self.button_img = button_img
		self.label = label
		self.adjustment = adjustment
		self.stop()
		self.thread = threading.Thread(target=self.update_position)
		self.thread.daemon = True
		self.thread.start()
		self.replace = time.time()
	def play(self,song=None,replace=True):
		if song == None:
			pygame.mixer.music.unpause()
			self.button_img.set_from_stock('gtk-media-pause',Gtk.IconSize.BUTTON)
			self.playing = True
		elif isinstance(song,Song):
			path = song.get_path()
			if path == False:
				self.replace = time.time()
				song.download(self.play,song,self.replace)
			elif replace == True or (replace == self.replace):
				self.song = song
				cover = self.song.get_cover()
				if cover:
					self.cover_obj.set_from_pixbuf(cover)
					self.cover_obj.show()
				else:
					self.cover_obj.hide()
				self.label.set_label(self.song.get_label())
				pygame.mixer.music.load(self.song.get_path())
				pygame.mixer.music.play();
				self.button_img.set_from_stock('gtk-media-pause',Gtk.IconSize.BUTTON)
				self.playing = True
				self.position = 0
				self.grid.show()
	def stop(self):
		self.grid.hide()
		pygame.mixer.music.pause()
		self.button_img.set_from_stock('gtk-media-play',Gtk.IconSize.BUTTON)
		self.song = False
		self.playing = False
		self.position = 0
	def pause(self):
		pygame.mixer.music.pause()
		self.button_img.set_from_stock('gtk-media-play',Gtk.IconSize.BUTTON)
		self.playing = False
	def toggle(self):
		if self.playing == True:
			self.pause()
		elif self.playing == False:
			self.play()
	def update_position(self):
		while True:
			if pygame.mixer.music.get_busy():
				value=self.position+pygame.mixer.music.get_pos()/10/self.song.get_duration()
				GLib.idle_add(self.adjustment.set_value,value)
			elif self.playing == True:
				self.stop()
			time.sleep(0.25)
	def go_position(self,value):
		pygame.mixer.music.play(0,self.song.get_duration()*value/100)
		self.position = value
