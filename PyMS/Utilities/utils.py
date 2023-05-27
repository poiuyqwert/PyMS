
from .PyMSError import PyMSError

from textwrap import wrap
import os, sys, platform, tempfile, errno

try:
	from _thread import start_new_thread
except:
	import threading
	def start_new_thread(target, args):
		threading.Thread(target=target, args=args).start()

WIN_REG_AVAILABLE = True
try:
	from winreg import *
except:
	WIN_REG_AVAILABLE = False

couriernew = ('Courier', -12, 'normal')

def is_windows():
	return (platform.system().lower() == 'windows')
def is_mac():
	return (platform.system().lower() == 'darwin')

# Decorator
def debug_func_log(should_log_call=None):
	def decorator(func):
		def do_log(*args, **kwargs):
			import uuid
			ref = uuid.uuid4().hex
			log = not should_log_call or should_log_call(func, args, kwargs)
			if log:
				print(("Func  : %s (%s)" % (func.__name__, ref)))
				print(("\tArgs  : %s" % (args,)))
				print(("\tkwargs: %s" % kwargs))
			result = func(*args, **kwargs)
			if log:
				print(("Func  : %s (%s)" % (func.__name__, ref)))
				print(("\tResult: %s" % (result,)))
			return result
		return do_log
	return decorator
def debug_state(states, history=[]):
	n = len(history)
	print(('##### %d: %s' % (n, states[n] if n < len(states) else 'Unknown')))
	history.append(None)

def nearest_multiple(v, m, r=round):
	return m * int(r(v / float(m)))

def register_registry(program_name, extension, file_type_name=None): # type: (str, str, str | None) -> None
	if not WIN_REG_AVAILABLE:
		raise PyMSError('Registry', 'You can currently only set as the default program on Windows machines.')
	def delkey(key,sub_key):
		try:
			h = OpenKey(key,sub_key)
		except WindowsError as e:
			if e.errno == 2:
				return
			raise
		except:
			raise
		try:
			while True:
				n = EnumKey(h,0)
				delkey(h,n)
		except EnvironmentError:
			pass
		h.Close()
		DeleteKey(key,sub_key)

	from . import Assets
	key = '%s:%s' % (program_name,extension)
	if file_type_name:
		file_type_name = ' ' + file_type_name
	else:
		file_type_name = ''
	if hasattr(sys, 'frozen'):
		executable = '"%s"' % sys.executable
	else:
		executable = '"%s" "%s"' % (sys.executable.replace('python.exe','pythonw.exe'), os.path.join(Assets.base_dir, '%s.pyw' % program_name))
	try:
		delkey(HKEY_CLASSES_ROOT, os.extsep + extension)
		delkey(HKEY_CLASSES_ROOT, key)
		SetValue(HKEY_CLASSES_ROOT, '.' + extension, REG_SZ, key)
		SetValue(HKEY_CLASSES_ROOT, key, REG_SZ, 'StarCraft%s *.%s file (%s)' % (file_type_name, extension, program_name))
		SetValue(HKEY_CLASSES_ROOT, key + '\\DefaultIcon', REG_SZ, Assets.image_path('%s.ico' % program_name))
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell', REG_SZ, 'open')
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell\\open\\command', REG_SZ, '%s --gui "%%1"' % executable)
	except:
		raise PyMSError('Registry', 'Could not complete file association.', capture_exception=True)
	from .UIKit import MessageBox
	MessageBox.showinfo('Success!', 'The file association was set.')

def flags(value, length):
	if isinstance(value, str):
		if len(value) != length or value.replace('0','').replace('1',''):
			raise PyMSError('Flags', 'Invalid flags')
		return sum(int(x)*(2**n) for n,x in enumerate(reversed(value)))
	return ''.join(reversed([str(value/(2**n)%2) for n in range(length)]))

def named_flags(flags, names, count, skip=0):
	header = ''
	values = ''
	for n in range(count):
		f = flags & (1 << n)
		name = 'Unknown%d' % n
		if n >= skip and n-skip < len(names) and names[n-skip]:
			name = names[n-skip]
		header += pad(name)
		values += pad(1 if f else 0)
	return (header,values)

def binary(flags, count):
	result = ''
	for n in range(count):
		result = ('1' if flags & (1 << n) else '0') + result
	return result

def flags_code(flags, name_map):
	names = []
	for (flag, name) in sorted(name_map.items(), key=lambda p: p[0]):
		if flags & flag:
			names.append(name)
	if not names:
		return 0
	return ' | '.join(names)

def fit(label, text, width=80, end=False, indent=0):
	r = label
	if not indent:
		s = len(r)
	else:
		s = indent
	indent = False
	for p in text.split('\n'):
		if p:
			for l in wrap(p, width - s):
				if indent:
					r += ' ' * s
				else:
					indent = True
				r += l
				r += '\n'
			r += '\n'
	return r.rstrip('\n') + ('\n' if end else '')

def float_to_str(value, strip_zero_decimals=True, max_decimals=4):
	result = str(value)
	if result.endswith('.0') and strip_zero_decimals:
		result = result[:-2]
	elif max_decimals is not None and '.' in result and len(result.split('.')[-1]) > max_decimals:
		result = result[:result.index('.') + max_decimals + 1]
	return result

def rpad(label, value='', span=20, padding=' '):
	label = str(label)
	return '%s%s%s' % (label, padding * (span - len(label)), value)
pad = rpad

def lpad(label, span=20, padding=' '):
	label = str(label)
	return '%s%s' % (padding * (span - len(label)), label)

def get_umask():
	umask = os.umask(0)
	os.umask(umask)
	return umask

BYTE_UNITS = ('B','KB','MB','GB')
def format_byte_size(bytes):
	value = bytes
	unit_id = 0
	while value / 1024.0 >= 1 and unit_id < len(BYTE_UNITS)-1:
		value = value / 1024.0
		unit_id += 1
	return float_to_str(value, max_decimals=2) + BYTE_UNITS[unit_id]

def create_temp_file(name, createmode=None):
	directory, filename = os.path.split(name)
	handle, temp_file = tempfile.mkstemp(prefix=".%s-" % filename, dir=directory)
	os.close(handle)

	try:
		mode = os.lstat(name).st_mode & 0o777
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise
		mode = createmode
		if mode is None:
			mode = ~get_umask()
		mode &= 0o666
	os.chmod(temp_file, mode)

	return temp_file

def start_file(filepath):
	if is_windows():
		os.startfile(filepath)
	else:
		cmd = 'open' if is_mac() else 'xdg-open'
		start_new_thread(os.system, ('%s "%s"' % (cmd, filepath),))

play_sound = None
try:
	from winsound import PlaySound, SND_MEMORY
	def win_play(raw_audio):
		start_new_thread(PlaySound, (raw_audio, SND_MEMORY))
	play_sound = win_play
except:
	import subprocess
	def osx_play(raw_audio):
		from . import Assets
		def do_play(path):
			try:
				subprocess.call(["afplay", temp_file])
			except:
				pass
			try:
				os.remove(path)
			except:
				pass
		temp_file = create_temp_file(Assets.internal_temp_file('audio'))
		handle = open(temp_file, 'wb')
		handle.write(raw_audio)
		handle.flush()
		os.fsync(handle.fileno())
		handle.close()
		start_new_thread(do_play, (temp_file,))
	play_sound = osx_play

class FFile:
	def __init__(self, bytes=True):
		self.data = b'' if bytes else ''

	def read(self):
		return self.data

	def write(self, data):
		self.data += data

	def close(self):
		pass
