
import tkFont as _Fonts

class Font(_Fonts.Font):
	@staticmethod
	def named(name):
		return _Fonts.nametofont(name)

	@staticmethod
	def families():
		return _Fonts.families()

	@staticmethod
	def names():
		return _Fonts.names()

	def __init__(self, family=None, size=None, bold=None, italic=None, underline=None, overstrike=None, name=None):
		options = {}
		if family != None:
			options['family'] = family
		if size != None:
			options['size'] = size
		if bold != None:
			options['weight'] = _Fonts.BOLD if bold else _Fonts.NORMAL
		if italic != None:
			options['slant'] = _Fonts.ITALIC if italic else _Fonts.ROMAN
		if underline != None:
			options['underline'] = underline
		if overstrike != None:
			options['overstrike'] = overstrike
		_Fonts.Font.__init__(self, name=name, **options)
