
from . import GAField

import urlparse, urllib, urllib2, platform, threading, time, sys


class GATarget:
	def track(self, data):
		raise NotImplementedError('%s.track' % self.__class__.__name__)

class GAOutputTarget:
	def track(self, data):
		print(data)


def os_bits():
	if sys.maxsize > 2**32:
		return 64
	elif sys.maxsize > 2**16:
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
	user_agent = 'Python%d/%s' % (bits, platform.python_version())
	system = os_name()
	version = os_version()
	if system == 'darwin':
		user_agent += ' (Macintosh; Intel Mac OS X %s)' % version.replace('.','_')
	elif system == 'windows':
		user_agent += ' (Windows NT %s%s)' % (version, '; WOW64' if bits == 64 else '')
	else:
		user_agent += ' (%s %s)' % (system, version)
	return user_agent

class GAAPITarget(threading.Thread):
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

	def __init__(self, protocol=None, host=None, collect_path=None, batch_path=None, debug_protocol=None, debug_path=None, useragent=None, debug=False):
		threading.Thread.__init__(self)
		self.daemon = True
		if debug:
			self._url_collect = urlparse.urlunparse((debug_protocol or GAAPITarget.DEBUG_PROTOCOL, host or GAAPITarget.HOST, debug_path or GAAPITarget.DEBUG_PATH, '', '', ''))
			self._url_batch = None
		else:
			self._url_collect = urlparse.urlunparse((protocol or GAAPITarget.PROTOCOL, host or GAAPITarget.HOST, collect_path or GAAPITarget.COLLECT_PATH, '', '', ''))
			self._url_batch = urlparse.urlunparse((protocol or GAAPITarget.PROTOCOL, host or GAAPITarget.HOST, batch_path or GAAPITarget.BATCH_PATH, '', '', ''))
		self._useragent = useragent or build_user_agent()
		self._track = []
		self._running = False
		self._paused = False
		self._pause_cond = threading.Condition(threading.Lock())
		self._pause()
		self._backlog = []
		# print(self._url_collect)
		# print(self._url_batch)
		# print(self._useragent)

	def _body(self, data):
		return urllib.urlencode(data)

	def _time(self):
		return int(time.time() * 1000)

	def _send(self, batch, body):
		try:
			# print(batch)
			# print(repr(body))
			request = urllib2.Request(self._url_batch if len(batch) > 1 else self._url_collect, body)
			request.add_header('User-Agent', self._useragent)
			_ = urllib2.urlopen(request)
			# print('done: ' + result.read())
			if self._backlog:
				retry_at = self._time()
				for data,failed_at in self._backlog:
					data[GAField.QueueTime] = retry_at - failed_at
					self._track.append(data)
		except urllib2.URLError:
			for data in batch:
				self._backlog.append((data, self._time()))
		except Exception:
			pass

	def run(self):
		while True:
			with self._pause_cond:
				while self._paused:
					self._pause_cond.wait()
					time.sleep(1)
				batch = []
				batch_body = ''
				batch_len = 0
				while self._track:
					track = self._track[0]
					body = self._body(track)
					body_len = len(body)
					if batch and body_len > GAAPITarget.BATCH_MAX_SINGLE_SIZE or body_len+batch_len > GAAPITarget.BATCH_MAX_TOTAL_SIZE:
						break
					del self._track[0]
					batch.append(track)
					if batch_body:
						batch_body += '\r\n'
						batch_len += 2
					batch_body += body
					batch_len += len(body)
					if not self._url_batch or len(batch) == GAAPITarget.BATCH_MAX_HITS or GAAPITarget.BATCH_MAX_TOTAL_SIZE-batch_len < GAAPITarget.BATCH_MAX_TOTAL_TOLERANCE:
						break
				if batch:
					self._send(batch, batch_body)
				if not self._track:
					self._pause()
			time.sleep(5)
	def _pause(self):
		if self._paused:
			return
		self._paused = True
		self._pause_cond.acquire()
	def _resume(self):
		if not self._paused:
			return
		self._paused = False
		self._pause_cond.notify()
		self._pause_cond.release()

	def track(self, data):
		if isinstance(data, dict):
			self._track.append(data)
		else:
			self._track.extend(data)
		if not self._running:
			self._running = True
			self.start()
		self._resume()
