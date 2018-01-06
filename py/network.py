#~ from gi.repository import Gtk, GdkPixbuf, Gdk, WebKit, GObject, GLib, Soup, Gio
import urllib2, threading, time, cookielib, json
from gi.repository import WebKit

class Network:
	def __init__(self,config):
		self.config = config
		self.user_agent = WebKit.WebSettings.get_user_agent(WebKit.WebSettings())
		if self.config["proxy"] != None:
			self.proxies = {'http': self.config["proxy"], 'https': self.config["proxy"]}
			self.proxy = urllib2.ProxyHandler(self.proxies)
		else:
			self.proxy = None
		self.urls = []
		self.thread = threading.Thread(target=self.background)
		self.thread.daemon = True
		self.thread.start()
	def go_direct(self,url):
		self.config.spinner.start()
		cj = cookielib.MozillaCookieJar()
		cookies = True
		try:
			if (self.check_cookies_file()):
				cj.load(COOKIES_FILE)
		except:
			cookies = False
		if self.config["proxy"] != None:
			opener = urllib2.build_opener(self.proxy,urllib2.HTTPCookieProcessor(cj))
		else:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		urllib2.install_opener(opener)
		req = urllib2.Request(url)
		req.add_header('User-Agent', self.user_agent)
		req.add_header('Referer', 'https://music.yandex.ua/')
		req.add_header('X-Retpath-Y', 'https%3A%2F%2Fmusic.yandex.ua%2')
		try:
			data = urllib2.urlopen(req, timeout=10)
			raw = data.read()
		except urllib2.HTTPError, e:
			raw = False
			print e.code
		except urllib2.URLError, e:
			raw = False
			print e.args
		if cookies == True:
			cj.save(COOKIES_FILE)
		self.config.spinner.stop()
		return raw
	def go(self,url,function,*args):
		if not isinstance(url,basestring):
			return False
		if not callable(function):
			return False
		self.thread = threading.Thread(target=self.go_threaded,args=([url,function,args]))
		self.thread.daemon = True
		self.thread.start()
		#~ self.urls.append([url,function,args])
		return True
	def go_threaded(self,url,function,args):
		function(self.go_direct(url),*args)
	def background(self):
		while True:
			#~ for i in self.urls:
				#~ GLib.idle_add(i[1],self.go_direct(i[0]),*i[2])
				#~ self.urls.remove(i)
			if len(self.urls) == 0:
				time.sleep(0.25)
			elif len(self.urls) == 1:
				i = self.urls[0]
				del self.urls[0]
				GLib.idle_add(i[1],self.go_direct(i[0]),*i[2])
			else:
				i = self.urls[0]
				del self.urls[0]
				GLib.idle_add(i[1],self.go_direct(i[0]),*i[2])
				i = self.urls[-1]
				del self.urls[-1]
				GLib.idle_add(i[1],self.go_direct(i[0]),*i[2])
	def check_cookies_file(self):
		if os.path.isfile(COOKIES_FILE):
			with open(COOKIES_FILE, 'r') as f:
				fl = f.readline()
				data = f.read()
			if (fl!='# Netscape HTTP Cookie File\n'):
				with open(COOKIES_FILE, 'wb') as f:
					f.write('# Netscape HTTP Cookie File\n' + fl + data)
					return True;
			else:
				return True;
		else:
			return False;
