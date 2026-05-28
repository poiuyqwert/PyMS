
from __future__ import annotations

from . import GAField, GATarget

import uuid

from typing import Self, Sequence

class GAData:
	def __init__(self, data: GATarget.EventData | None = None) -> None:
		self._data: GATarget.EventData
		if data is None:
			self._data = {}
		else:
			self._data = data.copy()

	def __setitem__(self, field: str, value: str) -> None:
		self._data[field] = value
	def set_data(self, data: GATarget.EventData) -> None:
		self._data = data.copy()
	def update_data(self, data: GATarget.EventData) -> None:
		self._data.update(data)

	def __getitem__(self, field: str) -> str | None:
		if not field in self._data:
			return None
		return self._data[field]
	def get_data(self) -> GATarget.EventData:
		return self._data.copy()

	def __delitem__(self, field: str) -> None:
		if field in self._data:
			del self._data[field]

	def set_application(self, name: str, version: str | None = None, appId: str | None = None, installerId: str | None = None) -> Self:
		self[GAField.App.Name] = name
		if version is not None:
			self[GAField.App.Version] = version
		if appId is not None:
			self[GAField.App.ID] = appId
		if installerId is not None:
			self[GAField.App.InstallerID] = installerId
		return self

	def __copy__(self) -> GAData:
		return self.copy()
	def __deepcopy__(self, memo: dict) -> GAData:
		return self.copy()
	def copy(self) -> GAData:
		return GAData(self._data)

class GAHit(GAData):
	TYPE: str | None = None

	def _build_data(self, data: GATarget.EventData) -> None:
		if self.TYPE is not None:
			data[GAField.HitType] = self.TYPE
	def tracking_data(self) -> GATarget.EventData:
		data = self._data.copy()
		self._build_data(data)
		return data

class GAScreen(GAHit):
	TYPE = 'screenview'

	def __init__(self, name: str, data: GATarget.EventData | None = None):
		GAHit.__init__(self, data)
		self.name = name

	def _build_data(self, data: GATarget.EventData) -> None:
		super()._build_data(data)
		data[GAField.Screen.Name] = self.name

	def copy(self) -> GAScreen:
		return GAScreen(self.name, self._data)

class GAEvent(GAHit):
	TYPE = 'event'

	def __init__(self, category: str, action: str, data: GATarget.EventData | None = None):
		GAHit.__init__(self, data)
		self.category = category
		self.action = action

	def _build_data(self, data: GATarget.EventData) -> None:
		super()._build_data(data)
		data[GAField.Event.Category] = self.category
		data[GAField.Event.Action] = self.action

	def copy(self) -> GAEvent:
		return GAEvent(self.category, self.action, self._data)

class GoogleAnalytics(GAData):
	def __init__(self, data: GATarget.EventData | None = None) -> None:
		GAData.__init__(self, data)
		self.enabled = True
		self._registered: dict[str, GAHit] = {}
		self.Custom = GAField.Custom()
		self.set_target(GATarget.GAAPITarget())
		self.tracking_id: str | None = None
		self.client_id: str = str(uuid.uuid4())

	def set_target(self, target: GATarget.GATarget) -> None:
		self._target = target

	def set_tracking_id(self, tracking_id: str) -> None:
		self.tracking_id = tracking_id
		# self[GAField.TrackingID] = tracking_id

	def set_client_id(self, client_id: str | None = None) -> str:
		if client_id is not None:
			self.client_id = client_id
		return self.client_id

	def _build_data(self, data: GATarget.EventData) -> None:
		if not GAField.Version in data:
			data[GAField.Version] = '1'
		if not GAField.TrackingID in data and self.tracking_id is not None:
			data[GAField.TrackingID] = self.tracking_id
		if not GAField.ClientID in data:
			data[GAField.ClientID] = self.client_id

	def _hit_data(self, hit: GAHit | GATarget.EventData):
		data = self._data.copy()
		self._build_data(data)
		if isinstance(hit, GAHit):
			data.update(hit.tracking_data())
		else:
			data.update(hit)
		return data

	def track(self, hit: GAHit | Sequence[GAHit]):
		if not self.enabled:
			return
		data: GATarget.EventData | list[GATarget.EventData]
		if isinstance(hit, GAHit):
			data = self._hit_data(hit)
		else: # If its not a GAHit we assume its an iterable of GAHit's
			data = [self._hit_data(h) for h in hit]
		self._target.track(data)

	# def register(self, name: str, hit: GAHit):
	# 	if hasattr(self, name) and not name in self._registered:
	# 		raise AttributeError(f"'{name}' is already an attribute so can\'t be registered")
	# 	self._registered[name] = hit
	# 	def _execute_registered(args, kwargs, self=self, hit=hit):
	# 		if kwargs is not None:
	# 			hit = hit.copy()
	# 			hit.update_data(kwargs)
	# 		self.track(hit)
	# 	setattr(self, name, lambda *args, **kwargs: _execute_registered(args, kwargs))

ga = GoogleAnalytics()
