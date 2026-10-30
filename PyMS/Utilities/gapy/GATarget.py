
from . import GAField

import urllib.parse, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, platform, threading, queue, time, sys

from typing import TypeAlias

EventData: TypeAlias = dict[str, str]

class GATarget:
	def track(self, data: EventData | list[EventData]) -> None:
		raise NotImplementedError(f'{self.__class__.__name__}.track')

class GAOutputTarget(GATarget):
	def track(self, data: EventData | list[EventData]):
		print(data)


def os_bits():
	if sys.maxsize > 2**32:
		return 64
	if sys.maxsize > 2**16:
		return 32
	return 16

def os_name():
	return platform.system().lower()

def os_version():
	if os_name() == 'darwin':
		return platform.mac_ver()[0]
	return platform.version()

def build_user_agent():
	bits = os_bits()
	user_agent = f'Python{bits}/{platform.python_version()}'
	system = os_name()
	version = os_version()
	if system == 'darwin':
		user_agent += f' (Macintosh; Intel Mac OS X {version.replace(".","_")})'
	elif system == 'windows':
		user_agent += f' (Windows NT {version}{"; WOW64" if bits == 64 else ""})'
	else:
		user_agent += f' ({system} {version})'
	return user_agent

class GAAPITarget(GATarget, threading.Thread):
	PROTOCOL = 'http'
	HOST = 'www.google-analytics.com'
	COLLECT_PATH = '/collect'
	BATCH_PATH = '/batch'
	DEBUG_PROTOCOL = 'https'
	DEBUG_PATH = '/debug/collect'

	BATCH_MAX_HITS = 20
	BATCH_MAX_SINGLE_SIZE = 8000
	BATCH_MAX_TOTAL_SIZE = 16000
	BATCH_MAX_TOTAL_TOLERANCE = 10

	def __init__(self, *, protocol=None, host=None, collect_path=None, batch_path=None, debug_protocol=None, debug_path=None, useragent=None, debug=False):
		threading.Thread.__init__(self)
		self.daemon = True
		if debug:
			self._url_collect = urllib.parse.urlunparse((debug_protocol or GAAPITarget.DEBUG_PROTOCOL, host or GAAPITarget.HOST, debug_path or GAAPITarget.DEBUG_PATH, '', '', ''))
			self._url_batch = None
		else:
			self._url_collect = urllib.parse.urlunparse((protocol or GAAPITarget.PROTOCOL, host or GAAPITarget.HOST, collect_path or GAAPITarget.COLLECT_PATH, '', '', ''))
			self._url_batch = urllib.parse.urlunparse((protocol or GAAPITarget.PROTOCOL, host or GAAPITarget.HOST, batch_path or GAAPITarget.BATCH_PATH, '', '', ''))
		self._useragent = useragent or build_user_agent()
		# Producer (caller) -> consumer (worker) handoff. Queue blocks the worker
		# while empty, so no separate pause/resume signalling is needed.
		self._track: queue.Queue[EventData] = queue.Queue()
		self._running = False
		# Only ever touched by the worker thread, so it needs no synchronization.
		self._backlog: list[tuple[EventData, int]] = []
		# print(self._url_collect)
		# print(self._url_batch)
		# print(self._useragent)

	def _body(self, data):
		return urllib.parse.urlencode(data)

	def _time(self):
		return int(time.time() * 1000)

	def _send(self, batch, body):
		try:
			# print(batch)
			# print(repr(body))
			request = urllib.request.Request(self._url_batch if len(batch) > 1 else self._url_collect, body.encode('utf-8'))
			request.add_header('User-Agent', self._useragent)
			with urllib.request.urlopen(request):
				pass
			# print('done: ' + result.read())
			if self._backlog:
				retry_at = self._time()
				for data,failed_at in self._backlog:
					data[GAField.QueueTime] = str(retry_at - failed_at)
					self._track.put(data)
				self._backlog = []
		except urllib.error.URLError:
			for data in batch:
				self._backlog.append((data, self._time()))
		except Exception:
			pass

	def run(self):
		# Item peeked from the queue but deferred to the next batch because it
		# didn't fit the current one (Queue has no peek, so we carry it over).
		carry: EventData | None = None
		while True:
			if carry is None:
				carry = self._track.get()
			batch = []
			batch_body = ''
			batch_len = 0
			while carry is not None:
				body = self._body(carry)
				body_len = len(body)
				if batch and (body_len > GAAPITarget.BATCH_MAX_SINGLE_SIZE or body_len+batch_len > GAAPITarget.BATCH_MAX_TOTAL_SIZE):
					break
				batch.append(carry)
				carry = None
				if batch_body:
					batch_body += '\r\n'
					batch_len += 2
				batch_body += body
				batch_len += len(body)
				if not self._url_batch or len(batch) == GAAPITarget.BATCH_MAX_HITS or GAAPITarget.BATCH_MAX_TOTAL_SIZE-batch_len < GAAPITarget.BATCH_MAX_TOTAL_TOLERANCE:
					break
				try:
					carry = self._track.get_nowait()
				except queue.Empty:
					break
			if batch:
				self._send(batch, batch_body)
			time.sleep(5)

	def track(self, data: EventData | list[EventData]):
		if isinstance(data, dict):
			self._track.put(data)
		else:
			for item in data:
				self._track.put(item)
		if not self._running:
			self._running = True
			self.start()
