
class FFile:
	def __init__(self):
		self.data = ''

	def read(self):
		return self.data

	def write(self, data):
		self.data += data

	def close(self):
		pass