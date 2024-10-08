
from .PyMSError import PyMSError

from textwrap import wrap
import os, sys, platform, tempfile, errno

from typing import Callable, Any, Sequence

try:
	from _thread import start_new_thread
except:
	import threading
	def start_new_thread(function: Callable[..., object], args: tuple[Any, ...], kwargs: dict[str, Any] = {}) -> int: # type: ignore[no-redef]
		thread = threading.Thread(target=function, args=args)
		thread.start()
		return thread.ident or 0

WIN_REG_AVAILABLE = True
try:
	from winreg import *
except:
	WIN_REG_AVAILABLE = False
	WindowsError = Exception
	def OpenKey(_a,_b) -> None:
		return None
	def EnumKey(_a,_b) -> None:
		return None
	def DeleteKey(_a,_b) -> None:
		pass
	HKEY_CLASSES_ROOT = ''
	REG_SZ = ''
	def SetValue(_a,_b,_c,_d) -> None:
		pass

# TODO: Remove
couriernew = ('Courier', -12, 'normal')
couriernew_bold = ('Courier New', -11, 'bold')

def is_windows() -> bool:
	return (platform.system().lower() == 'windows')

def is_mac() -> bool:
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

def nearest_multiple(v: int, m: int, r: Callable[[float], float] = round) -> int:
	return m * int(r(v / float(m)))

def register_registry(program_name: str, extension: str, file_type_name: str | None = None) -> None:
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

def flags(value: int | str, length: int) -> str:
	if isinstance(value, str):
		if len(value) != length or value.replace('0','').replace('1',''):
			raise PyMSError('Flags', 'Invalid flags')
		return sum(int(x)*(2**n) for n,x in enumerate(reversed(value)))
	return ''.join(reversed([str(value/(2**n)%2) for n in range(length)]))

def named_flags(flags: int, names: Sequence[str | None], count: int, skip: int = 0) -> tuple[str, str]:
	header = ''
	values = ''
	for n in range(count):
		f = flags & (1 << n)
		name = 'Unknown%d' % n
		if n >= skip and n-skip < len(names):
			possible_name = names[n-skip]
			if possible_name:
				name = possible_name
		header += pad(name)
		values += pad('1' if f else '0')
	return (header,values)

def binary(flags: int, count: int) -> str:
	result = ''
	for n in range(count):
		result = ('1' if flags & (1 << n) else '0') + result
	return result

def flags_code(flags: int, name_map: dict[int, str]) -> str:
	names = []
	for (flag, name) in sorted(name_map.items(), key=lambda p: p[0]):
		if flags & flag:
			names.append(name)
	if not names:
		return '0'
	return ' | '.join(names)

def fit(label: str, text: str, width: int = 80, end: bool = False, indent: int = 0) -> str:
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

def fit2(text: str, width: int = 80, indent: str | int = '', label: str | None = None) -> str:
	if isinstance(indent, int):
		break_indent = ' ' * indent
	else:
		break_indent = indent
	label_indent = ''
	if label:
		label_indent = ' ' * len(label)
	label_line_width = width - len(label_indent)
	break_line_width = label_line_width - len(break_indent)
	result = ''
	first_line = True
	for line in text.splitlines():
		if line:
			if first_line and label:
				result += label
			else:
				result += label_indent
			line_width = label_line_width
			if len(line) > line_width:
				add_space = False
				for word in line.split(' '):
					if len(word) < line_width:
						if add_space:
							result += ' '
						result += word
						line_width -= len(word) + 1
						add_space = True
					else:
						line_width = break_line_width - len(word)
						result += '\n' + label_indent + break_indent + word
			else:
				result += line
			result += '\n'
		else:
			result += '\n'
		first_line = False
	return result[:-1]

def float_to_str(value: float, strip_zero_decimals: bool = True, max_decimals: int = 4) -> str:
	result = str(value)
	if result.endswith('.0') and strip_zero_decimals:
		result = result[:-2]
	elif max_decimals is not None and '.' in result and len(result.split('.')[-1]) > max_decimals:
		result = result[:result.index('.') + max_decimals + 1]
	return result

def rpad(label: str, value: str = '', span: int = 20, padding: str = ' ') -> str:
	label = str(label)
	return '%s%s%s' % (label, padding * (span - len(label)), value)
pad = rpad

def lpad(label: str, span: int = 20, padding: str = ' ') -> str:
	label = str(label)
	return '%s%s' % (padding * (span - len(label)), label)

def get_umask() -> int:
	umask = os.umask(0)
	os.umask(umask)
	return umask

BYTE_UNITS = ('B','KB','MB','GB')
def format_byte_size(bytes: float) -> str:
	value = bytes
	unit_id = 0
	while value / 1024.0 >= 1 and unit_id < len(BYTE_UNITS)-1:
		value = value / 1024.0
		unit_id += 1
	return float_to_str(value, max_decimals=2) + BYTE_UNITS[unit_id]

def create_temp_file(name: str, createmode: int | None = None) -> str:
	directory, filename = os.path.split(name)
	handle, temp_file = tempfile.mkstemp(prefix=".%s-" % filename, dir=directory)
	os.close(handle)

	try:
		mode = os.lstat(name).st_mode & 0o777
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise
		if createmode is None:
			mode = ~get_umask()
		else:
			mode = createmode
		mode &= 0o666
	os.chmod(temp_file, mode)

	return temp_file

def start_file(filepath: str) -> None:
	if hasattr(os, 'startfile'):
		os.startfile(filepath)
	else:
		cmd = 'open' if is_mac() else 'xdg-open'
		start_new_thread(os.system, ('%s "%s"' % (cmd, filepath),))

play_sound: Callable[[bytes], None] | None = None
try:
	from winsound import PlaySound, SND_MEMORY # type: ignore[attr-defined]
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
