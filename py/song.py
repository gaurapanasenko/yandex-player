import os, json, md5
from gi.repository import GdkPixbuf
from mutagen.id3 import ID3NoHeaderError, ID3, TPE1, TIT2, COMM, TALB, APIC
from shutil import copyfile

class Song:
	def __init__(self,config,albumid,trackid,artist,album,track,cover,duration,bigcover):
		self.config = config
		if isinstance(albumid,str) and albumid.isdigit():
			self.albumid = int(albumid)
		elif isinstance(albumid,int):
			self.albumid = albumid
		else:
			raise ValueError("albumid must be number")
		if isinstance(trackid,str) and trackid.isdigit():
			self.trackid = int(trackid)
		elif isinstance(trackid,int):
			self.trackid = trackid
		else:
			raise ValueError("trackid must be number")
		if isinstance(artist,str):
			self.artist = artist
		else:
			raise TypeError("artist must be string")
		if isinstance(album,str):
			self.album = album
		else:
			raise TypeError("album must be string")
		if isinstance(track,str):
			self.track = track
		else:
			raise TypeError("track must be string")
		if isinstance(cover,GdkPixbuf.Pixbuf) or cover == None:
			self.cover = cover
		else:
			cover = False
			#~ raise TypeError("cover must be GdkPixbuf.Pixbuf or bool")
		if isinstance(duration,str) and duration.isdigit():
			self.duration = int(duration)
		elif isinstance(duration,int):
			self.duration = duration
		else:
			raise ValueError("duration must be number")
		if isinstance(bigcover,str):
			self.bigcover = bigcover
		else:
			raise TypeError("bigcover must be string")
	def download(self,on_finish=None,*args):
		url = 'https://music.yandex.ua/api/v2.1/handlers/track/' + str(self.trackid) + ':' + str(self.albumid) + '/web-search-album-album-main/download/m'
		self.config.network.go(url,self.download_event,on_finish,0,*args)
	def download_event(self,data,on_finish=None,stage=0,*args):
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
		path = self.config.temp_folder + "/" + str(self.albumid) + "_" + str(self.trackid) + ".mp3"
		if os.path.isfile(path):
			return str(path)
		else:
			return False
	def get_duration(self):
		return self.duration
	def get_label(self):
		return self.artist + " - " + self.track
	def get_cover(self):
		return self.cover
	def save(self,path):
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
		data = self.config.network.go_direct(self.bigcover)
		audio['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=data)
		audio.save(tmp_path)
		copyfile(tmp_path,path)
		return True
