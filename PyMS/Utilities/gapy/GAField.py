
Version = 'v'
HitType = 't'
TrackingID = 'tid'
ClientID = 'cid'
UserID = 'uid'
QueueTime = 'qt'

class App:
	Name = 'an'
	ID = 'aid'
	Version = 'av'
	InstallerID = 'aiid'

	def __init__(self):
		raise NotImplementedError

class Event:
	Category = 'ec'
	Action = 'ea'
	Label = 'el'
	Value = 'ev'

	def __init__(self):
		raise NotImplementedError

class Screen:
	Name = 'cd'

class Custom:
	@staticmethod
	def Dimension(n):
		return 'cd%d' % n

	@staticmethod
	def Metric(n):
		return 'cm%d' % n

	def __init__(self):
		self._registered = set()

	def register(self, n, name):
		if hasattr(self, name) and not name in self._registered:
			raise AttributeError("'%s' is already an attribute so can\'t be registered" % name)
		setattr(self, name, 'cd%d' % n)
		self._registered.add(name)