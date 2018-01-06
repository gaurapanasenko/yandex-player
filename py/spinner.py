class Spinner:
	def __init__(self,obj):
		self.spinner = obj
		self.count = 0
	def gui(self):
		if self.count > 0:
			self.spinner.start()
		else:
			self.spinner.stop()
	def start(self):
		self.count+=1
		self.gui()
	def stop(self):
		self.count-=1
		self.gui()
