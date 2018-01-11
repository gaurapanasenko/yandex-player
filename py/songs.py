from py.song import Song
from gi.repository import Gio, GdkPixbuf

class Songs:
	def __init__(self,config):
		self.config = config
		self.songs = []
		self.model = self.config.builder.get_object('treestore')
		self.model.clear()
		self.cover_queue = {}
		self.cover_cache = {}
	def append(self,parent,data):
		song = Song(self.config,data)
		if song.is_valid():
			parentItem = None
			if isinstance(parent,int) and parent < len(self.songs):
				parentItem = self.songs[parent][1]
			item = self.model.append(parentItem,song.get_data())
			self.songs.append([song,item])
			index = len(self.songs) - 1
			song.set_index(index)
			self.model.set(item,0,index)
			self.load_cover(song.get_cover_url().replace("%%","50x50"),index)
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
	def load_cover(self,url,index = None):
		if not isinstance(url,basestring) or url[0:8] != 'https://':
			return
		if url in self.cover_cache:
			self.set_cover(index,self.cover_cache[url])
		elif url in self.cover_queue and index not in self.cover_queue[url]:
			self.cover_queue[url].append(index)
		else:
			self.cover_queue[url] = [index]
			self.config.network.go(url,self.on_cover_received)
	def set_cover(self,index,pixbuf):
		self.songs[index][0].set_cover(pixbuf)
		self.model.set(self.songs[index][1],1,pixbuf)
	def on_cover_received(self, url, data, count = 0):
		if not isinstance(data,str) or data == "":
			#~ if count < 10:
				#~ self.config.network.go(url,self.on_cover_received,count+1)
			return False
		input_stream = Gio.MemoryInputStream.new_from_data(data, None)
		pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream, None)
		self.cover_cache[url] = pixbuf
		for i in self.cover_queue[url]:
			self.set_cover(i,pixbuf)
		del self.cover_queue[url]
	def activate(self, path):
		item = self.model.get_iter(path)
		song = self.songs[self.model.get_value(item,0)][0]
		song_type = song.get_type()
		if song_type == "song":
			self.config.player.play(song)
