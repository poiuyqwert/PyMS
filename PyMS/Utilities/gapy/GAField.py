
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

	def __init__(self) -> None:
		raise NotImplementedError

class Event:
	Category = 'ec'
	Action = 'ea'
	Label = 'el'
	Value = 'ev'

	def __init__(self) -> None:
		raise NotImplementedError

class Screen:
	Name = 'cd'

class Custom:
	@staticmethod
	def Dimension(n):
		return f'cd{n}'

	@staticmethod
	def Metric(n):
		return f'cm{n}'

	def __init__(self) -> None:
		self._registered: set[str] = set()

	def register(self, n: int, name: str) -> str:
		if hasattr(self, name) and not name in self._registered:
			raise AttributeError(f"'{name}' is already an attribute so can\'t be registered")
		# setattr(self, name, 'cd%d' % n)
		self._registered.add(name)
		return Custom.Dimension(n)
