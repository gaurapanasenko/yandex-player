import os, json, md5
from gi.repository import GdkPixbuf
from mutagen.id3 import ID3NoHeaderError, ID3, TPE1, TIT2, COMM, TALB, APIC
from shutil import copyfile

class Song:
	def __init__(self,config,data):
		self.config = config
		self.index = None
		self.song_type = None
		self.artistid = None
		self.artist = ""
		self.albumid = None
		self.album = ""
		self.trackid = None
		self.track = ""
		self.duration = None
		self.cover_url = None
		self.cover = None
		if 'artistid' not in data and 'artist' not in data: return
		if 'artistid' in data:
			try:
				self.artistid = int(data['artistid'])
			except: return
		if 'artist' in data:
			self.artist = str(data['artist'].encode('utf-8'))

		if bool('albumid' not in data) != bool('album' not in data): return
		if 'albumid' in data:
			try:
				self.albumid = int(data['albumid'])
			except: return
		if 'album' in data:
			self.album = str(data['album'].encode('utf-8'))

		if bool('trackid' not in data) != bool('track' not in data): return
		if 'trackid' in data:
			try:
				self.trackid = int(data['trackid'])
			except: return
		if 'track' in data:
			self.track = str(data['track'].encode('utf-8'))

		if self.artistid is not None and self.albumid is None and self.trackid is None:
			self.song_type = 'artist'
		elif self.artistid is not None and self.albumid is not None and self.trackid is None:
			self.song_type = 'album'
		elif self.artistid is not None and self.albumid is not None and self.trackid is not None:
			self.song_type = 'song'
		else: return

		if 'cover' in data and isinstance(data['cover'],GdkPixbuf.Pixbuf):
			self.cover = cover
		else:
			self.cover = None

		if 'cover_url' in data:
			self.cover_url = str(data['cover_url'])

		if 'duration' in data:
			try:
				self.duration = int(data['duration'])
			except: pass

	def is_valid(self):
		return self.song_type != None

	def get_type(self):
		return self.song_type

	def get_duration(self):
		return self.duration

	def get_string_duration(self):
		if self.duration is None: return None
		else:
			return str(self.duration/60) + ':' + str(self.duration/10%6)+str(self.duration%10)

	def get_cover_url(self):
		return self.cover_url

	def set_cover(self, pixbuf):
		self.cover = pixbuf

	def get_cover(self):
		return self.cover

	def set_index(self, index):
		self.index = index

	def get_index(self):
		return self.index

	def get_label(self):
		if self.song_type != "song":
			return False
		return self.artist + " - " + self.track

	def get_data(self):
		return [self.index,self.cover,self.artist,self.album,self.track,self.get_string_duration()]

	def download(self,on_finish=None,*args):
		if self.song_type != "song":
			return False
		url = 'https://music.yandex.ua/api/v2.1/handlers/track/' + str(self.trackid) + ':' + str(self.albumid) + '/web-search-album-album-main/download/m'
		self.config.network.go(url,self.download_event,on_finish,0,*args)

	def download_event(self,url,data,on_finish=None,stage=0,*args):
		if self.song_type != "song":
			return False
		if stage == 0:
			dt = json.loads(data)
			self.config.network.go(str(dt['src'] + "&format=json"),self.download_event,on_finish,1,*args)
		elif stage == 1:
			dt = json.loads(data)
			url = 'https://' + dt['host'] + '/get-mp3/' + md5.new('XGRlBW9FXlekgbPrRHuSiA' + dt['path'][1:] + dt['s']).hexdigest() + '/' + dt['ts'] + dt['path'] + '?track-id=' + str(self.trackid)
			self.config.network.go(str(url),self.download_event,on_finish,2,*args)
		elif stage == 2 and data != False:
			file = open(self.config.temp_folder + "/" + str(self.albumid) + "_" + str(self.trackid) + ".mp3", 'w')
			file.write(data)
			file.close()
			if callable(on_finish):
				on_finish(*args)
		else:
			return False

	def get_path(self):
		if self.song_type != "song":
			return False
		path = self.config.temp_folder + "/" + str(self.albumid) + "_" + str(self.trackid) + ".mp3"
		if os.path.isfile(path):
			return str(path)
		else:
			return False

	def save(self,path):
		if self.song_type != "song":
			return False
		tmp_path = self.get_path()
		if tmp_path == False:
			return False
		try:
			audio = ID3(tmp_path)
		except ID3NoHeaderError:
			audio = ID3()
		audio['TIT2'] = TIT2(encoding=3, text=str(self.track).decode('utf-8'))
		audio['TPE1'] = TPE1(encoding=3, text=str(self.artist).decode('utf-8'))
		audio['TALB'] = TALB(encoding=3, text=str(self.album).decode('utf-8'))
		data = self.config.network.go_direct(self.cover_url.replace("%%","400x400"))
		audio['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=data)
		audio.save(tmp_path)
		copyfile(tmp_path,path)
		return True
