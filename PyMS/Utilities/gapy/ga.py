
from . import GAField, GATarget

import platform, uuid

class GAData:
	def __init__(self, data=None):
		if data == None:
			self._data = {}
		else:
			self._data = data.copy()

	def __setitem__(self, field, value):
		self._data[field] = value
	def set_data(self, data):
		self._data = data.copy()
	def update_data(self, data):
		self._data.update(data)

	def __getitem__(self, field):
		if not field in self._data:
			return None
		return self._data[field]
	def get_data(self):
		return self._data.copy()

	def __delitem__(self, field):
		if field in self._data:
			del self._data[field]

	def set_application(self, name, version=None, appId=None, installerId=None):
		self[GAField.App.Name] = name
		if version != None:
			self[GAField.App.Version] = version
		if appId != None:
			self[GAField.App.ID] = appId
		if installerId != None:
			self[GAField.App.InstallerID] = installerId
		return self

	def __copy__(self):
		return self.copy()
	def __deepcopy__(self, memo):
		return self.copy()
	def copy(self):
		return GAData(self._data)

class GAHit(GAData):
	TYPE = None

	def _build_data(self, data):
		if self.TYPE != None:
			data[GAField.HitType] = self.TYPE
	def tracking_data(self):
		data = self._data.copy()
		self._build_data(data)
		return data

class GAScreen(GAHit):
	TYPE = 'screenview'

	def __init__(self, name, data=None):
		GAHit.__init__(self, data)
		self[GAField.Screen.Name] = name

	def copy(self):
		return GAScreen(self[GAField.Screen.Name], self._data)

class GAEvent(GAHit):
	TYPE = 'event'

	def __init__(self, category, action, data=None):
		GAHit.__init__(self, data)
		self[GAField.Event.Category] = category
		self[GAField.Event.Action] = action

	def copy(self):
		return GAEvent(self[GAField.Event.Category], self[GAField.Event.Action], self._data)

class GoogleAnalytics(GAData):
	def __init__(self, data=None):
		GAData.__init__(self, data)
		self.enabled = True
		self._registered = {}
		self.Custom = GAField.Custom()
		self.set_target(GATarget.GAAPITarget())

	def set_target(self, target):
		self._target = target
	def set_tracking_id(self, tracking_id):
		self[GAField.TrackingID] = tracking_id
	def set_client_id(self, client_id=None):
		if client_id == None:
			client_id = str(uuid.uuid4())
		self[GAField.ClientID] = client_id
		return client_id

	def _build_data(self, data):
		if not GAField.Version in data:
			data[GAField.Version] = '1'
	def _hit_data(self, hit):
		data = self._data.copy()
		self._build_data(data)
		if isinstance(hit, GAHit):
			data.update(hit.tracking_data())
		else:
			data.update(hit)
		return data
	def track(self, hit):
		if not self.enabled:
			return
		data = None
		if isinstance(hit, GAHit):
			data = self._hit_data(hit)
		else: # If its not a GAHit we assume its an iterable of GAHit's
			data = [self._hit_data(h) for h in hit]
		self._target.track(data)

	def register(self, name, hit):
		if hasattr(self, name) and not name in self._registered:
			raise AttributeError("'%s' is already an attribute so can\'t be registered" % name)
		self._registered[name] = hit
		def _execute_registered(args, kwargs, self=self, hit=hit):
			if kwargs != None:
				hit = hit.copy()
				hit.update_data(kwargs)
			self.track(hit)
		setattr(self, name, lambda *args, **kwargs: _execute_registered(args, kwargs))

ga = GoogleAnalytics()

if __name__ == '__main__':
	# ga.set_target(GATarget.GAAPITarget(debug=True))
	ga.set_tracking_id('UA-42320973-3')
	print(ga.set_client_id()) #'80d7d928-8946-443c-845c-49039ef671f8')
	ga.set_application('PyGRP', '4.0.0')
	ga.Custom.register(1, 'PYMS_VERSION')
	ga.Custom.register(2, 'PYTHON_VERSION')
	ga.Custom.register(3, 'OS_NAME')
	ga.Custom.register(4, 'OS_VERSION')
	ga.Custom.register(5, 'OS_BITS')
	ga[ga.Custom.PYMS_VERSION] = '1.2.3'
	ga[ga.Custom.PYTHON_VERSION] = platform.python_version()
	ga[ga.Custom.OS_NAME] = GATarget.os_name()
	ga[ga.Custom.OS_VERSION] = GATarget.os_version()
	ga[ga.Custom.OS_BITS] = GATarget.os_bits()
	ga.track(GAScreen('main'))
	import time
	time.sleep(5)
