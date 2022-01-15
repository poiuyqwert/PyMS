
from ...Utilities.UIKit import Frame

class CodeGeneratorEditor(Frame):
	def __init__(self, parent, generator):
		self.generator = generator
		Frame.__init__(self, parent)

	def save(self):
		raise NotImplementedError(self.__class__.__name__ + '.save()')

class CodeGeneratorType(object):
	TYPES = {}
	TYPE = None

	@classmethod
	def validate(cls, save):
		raise NotImplementedError(cls.__name__ + '.validate()')

	def __init__(self, save=None):
		pass

	# None for infinite
	def count(self):
		raise NotImplementedError(self.__class__.__name__ + '.count()')

	def value(self, lookup_value):
		raise NotImplementedError(self.__class__.__name__ + '.value()')

	def description(self):
		raise NotImplementedError(self.__class__.__name__ + '.description()')

	def save(self):
		return {'type': self.TYPE}
