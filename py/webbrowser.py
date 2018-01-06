# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*
from gi.repository import WebKit, Soup

class WebBrowser:
	def __init__(self, config, box):
		webkit = WebKit
		session = webkit.get_default_session()
		cookiejar = Soup.CookieJarText.new(config.cookies_file, False)
		cookiejar.set_accept_policy(Soup.CookieJarAcceptPolicy.ALWAYS)
		session.add_feature(cookiejar)
		if self.config["proxy"] is not None:
			session.set_property('proxy-uri',Soup.URI.new('http://' + self.config["proxy"]))
		self.webview = webkit.WebView()
		self.webview.connect("title-changed", config.signals.on_webbrowser_changed)
		self.webview.load_uri('https://music.yandex.ru/')
		self.box = box
		box.add(self.webview)
		self.webview.show()
	def getView(self):
		return self.webview
	def isCapchaPage(self):
		return self.webview.get_title()=="Ой!"
	def __del__(self):
		self.box.remove(self.webview)
		del self.webview
