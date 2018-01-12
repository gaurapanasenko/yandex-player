from py.song import Song
from gi.repository import Gio, GdkPixbuf
import json

class Songs:
	def __init__(self,config):
		self.config = config
		self.songs = []
		self.model = self.config.builder.get_object('treestore')
		self.model.clear()
		self.view = self.config.builder.get_object('treeview')
		self.cover_state = {}
		self.cover_queue = {}
		self.cover_cache = {}
	def append(self,parent,data):
		song = Song(self.config,data)
		if song.is_valid():
			parentItem = None
			if isinstance(parent,int) and parent < len(self.songs) and parent >= 0:
				parentItem = self.songs[parent][1]
			item = self.model.append(parentItem,song.get_data())
			self.songs.append([song,item,parent])
			index = len(self.songs) - 1
			song.set_index(index)
			self.model.set(item,0,index)
			if song.get_cover_url() != None:
				self.append_cover_queue(song.get_cover_url().replace("%%","50x50"),index)
			return index
		return False;
	def clear(self):
		self.model.clear()
		del self.songs[:]
		self.cover_queue.clear()
	def is_exists(song):
		if isinstance(song,Song):
			return self.songs[song.get_index()][0] == song
		else:
			False
	def load_covers(self,index):
		for i in self.songs:
			if i[2] == int(index) and i[0].get_cover_url() != None:
				self.load_cover(i[0].get_cover_url().replace("%%","50x50"))
	def append_cover_queue(self,url,index):
		if not isinstance(url,basestring) or url[0:8] != 'https://':
			return
		if url not in self.cover_queue:
			self.cover_queue[url] = [index]
			self.cover_state[url] = -1
		elif index not in self.cover_queue[url]:
			self.cover_queue[url].append(index)
		if url in self.cover_cache:
			self.set_cover(index,self.cover_cache[url])
	def load_cover(self,url):
		if url in self.cover_cache:
			self.set_queue_covers(url)
		elif url in self.cover_state and self.cover_state[url] == -1:
			self.cover_state[url] == 0
			self.config.network.go(url,self.on_cover_received)
	def set_cover(self,index,pixbuf):
		self.songs[index][0].set_cover(pixbuf)
		self.model.set(self.songs[index][1],1,pixbuf)
	def set_queue_covers(self,url):
		if url in self.cover_cache:
			pixbuf = self.cover_cache[url]
			for i in self.cover_queue[url]:
				self.set_cover(i,pixbuf)
	def on_cover_received(self, url, data, count = 0):
		if not isinstance(data,str) or data == "":
			if count < 10:
				self.config.network.go(url,self.on_cover_received,count + 1)
			return False
		input_stream = Gio.MemoryInputStream.new_from_data(data, None)
		pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
		self.cover_cache[url] = pixbuf
		self.cover_state[url] = 1
		self.set_queue_covers(url)
	def activate(self, path, index = None, toggle_row = True):
		if path != None:
			item = self.model.get_iter(path)
			index = self.model.get_value(item,0)
		if index == None:
			return False
		song = self.songs[index][0]
		song_type = song.get_type()
		if song_type == "song":
			self.config.player.play(song)
		elif song_type == "artist":
			if song.get_all_songs() == False:
				self.config.network.go("https://music.yandex.ua/handlers/artist.jsx?artist=" + str(song.get_artist_id()) + "&what=tracks",self.set_from_json,index)
		elif song_type == "album":
			if song.get_all_songs() == False:
				self.config.network.go("https://music.yandex.ua/handlers/album.jsx?album=" + str(song.get_album_id()),self.set_from_json,index)
		elif song_type == "info":
			self.activate(None,self.songs[index][2],False)
		if toggle_row == True:
			self.toggle_row(index)
	def set_from_json(self, url, json_data, parent = None):
		if json_data == False:
			return False
		if ('<!DOCTYPE html>' == json_data[0:15]):
			self.captcha()
			return False
		data = json.loads(json_data)
		if parent == None:
			self.config.songs.clear()
			for i in data['artists']['items']:
				parentItem = self.config.songs.append(-1,{
					'artistid': i['id'],
					'artist': i['name'],
					'cover_url': str('https://' + i['cover']['uri']) if 'cover' in i else None
				})
				parentItem = self.config.songs.append(parentItem,{
					'artistid': -1,
					'artist': "Popular tracks",
				})
				for j in i['popularTracks']:
					self.config.songs.append(parentItem,{
						'artistid': i['id'],
						'artist': i['name'],
						'albumid': j['albums'][0]['id'],
						'album': j['albums'][0]['title'],
						'trackid': j['id'],
						'track': j['title'],
						'duration': j['durationMs']/1000,
						'cover_url': str('https://' + j['albums'][0]['coverUri']) if 'coverUri' in j['albums'][0] else None
					})
			for i in data['albums']['items']:
				parentItem = self.config.songs.append(-1,{
					'artistid': i['artists'][0]['id'],
					'artist': i['artists'][0]['name'],
					'albumid': i['id'],
					'album': i['title'],
					'cover_url': str('https://' + i['coverUri']) if 'coverUri' in i else None
				})
			for j in data['tracks']['items']:
				self.config.songs.append(-1,{
					'artistid': j['artists'][0]['id'],
					'artist': j['artists'][0]['name'],
					'albumid': j['albums'][0]['id'],
					'album': j['albums'][0]['title'],
					'trackid': j['id'],
					'track': j['title'],
					'duration': j['durationMs']/1000,
					'cover_url': str('https://' + j['albums'][0]['coverUri']) if 'coverUri' in j['albums'][0] else None
				})
			self.load_covers(-1)
		elif self.songs[parent][0].get_type() == "artist":
			self.songs[parent][0].set_all_songs(True)
			parent_albums = self.config.songs.append(parent,{
				'artistid': -1,
				'artist': "Albums",
			})
			parent_tracks = self.config.songs.append(parent,{
				'artistid': -1,
				'artist': "Tracks",
			})
			for i in data['albums']:
				parentItem = self.config.songs.append(parent_albums,{
					'artistid': data['artist']['id'],
					'artist': data['artist']['name'],
					'albumid': i['id'],
					'album': i['title'],
					'cover_url': str('https://' + i['coverUri']) if 'coverUri' in i else None
				})
			for j in data['tracks']:
				self.config.songs.append(parent_tracks,{
					'artistid': j['artists'][0]['id'],
					'artist': j['artists'][0]['name'],
					'albumid': j['albums'][0]['id'],
					'album': j['albums'][0]['title'],
					'trackid': j['id'],
					'track': j['title'],
					'duration': j['durationMs']/1000,
					'cover_url': str('https://' + j['albums'][0]['coverUri']) if 'coverUri' in j['albums'][0] else None
				})
			self.view.expand_row(self.model.get_path(self.songs[parent][1]),False)
		elif self.songs[parent][0].get_type() == "album":
			for i in data['volumes']:
				for j in i:
					self.config.songs.append(parent,{
						'artistid': j['artists'][0]['id'],
						'artist': j['artists'][0]['name'],
						'albumid': data['id'],
						'album': data['title'],
						'trackid': j['id'],
						'track': j['title'],
						'duration': j['durationMs']/1000,
						'cover_url': str('https://' + data['coverUri']) if 'coverUri' in data else None
					})
			self.view.expand_row(self.model.get_path(self.songs[parent][1]),False)
	def toggle_row(self,index):
		path = self.model.get_path(self.songs[index][1])
		if self.view.row_expanded(path) == False:
			self.view.expand_row(path,False)
		else: self.view.collapse_row(path)
