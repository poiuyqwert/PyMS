
from textwrap import wrap
import os, platform, subprocess, tempfile, errno

from typing import Callable, Any, Sequence

try:
	from _thread import start_new_thread
except Exception:
	import threading
	def start_new_thread(function: Callable[..., object], args: tuple[Any, ...], kwargs: dict[str, Any] | None = None) -> int: # type: ignore[no-redef]
		thread = threading.Thread(target=function, args=args, kwargs=kwargs)
		thread.start()
		return thread.ident or 0

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
				print(f"Func  : {func.__name__} ({ref})")
				print(f"\tArgs  : {args}")
				print(f"\tkwargs: {kwargs}")
			result = func(*args, **kwargs)
			if log:
				print(f"Func  : {func.__name__} ({ref})")
				print(f"\tResult: {result}")
			return result
		return do_log
	return decorator
def debug_state(states):
	n = getattr(debug_state, '_count', 0)
	print(f'##### {n}: {states[n] if n < len(states) else "Unknown"}')
	debug_state._count = n + 1 # type: ignore[attr-defined] # pylint: disable=protected-access

def nearest_multiple(v: int, m: int, r: Callable[[float], float] = round) -> int:
	return m * int(r(v / float(m)))

def named_flags(value: int, names: Sequence[str | None], count: int, skip: int = 0) -> tuple[str, str]:
	header = ''
	values = ''
	for n in range(count):
		f = value & (1 << n)
		name = f'Unknown{n}'
		if n >= skip and n-skip < len(names):
			possible_name = names[n-skip]
			if possible_name:
				name = possible_name
		header += pad(name)
		values += pad('1' if f else '0')
	return (header,values)

def binary(value: int, count: int) -> str:
	result = ''
	for n in range(count):
		result = ('1' if value & (1 << n) else '0') + result
	return result

def flags_code(value: int, name_map: dict[int, str]) -> str:
	names = []
	for (flag, name) in sorted(name_map.items(), key=lambda p: p[0]):
		if value & flag:
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
	elif max_decimals is not None and '.' in result and len(result.rsplit('.', maxsplit=1)[-1]) > max_decimals:
		result = result[:result.index('.') + max_decimals + 1]
	return result

def rpad(label: str, value: str = '', span: int = 20, padding: str = ' ') -> str:
	label = str(label)
	return f'{label}{padding * (span - len(label))}{value}'
pad = rpad

def lpad(label: str, span: int = 20, padding: str = ' ') -> str:
	label = str(label)
	return f'{padding * (span - len(label))}{label}'

def get_umask() -> int:
	umask = os.umask(0)
	os.umask(umask)
	return umask

BYTE_UNITS = ('B','KB','MB','GB')
def format_byte_size(size: float) -> str:
	value = size
	unit_id = 0
	while value / 1024.0 >= 1 and unit_id < len(BYTE_UNITS)-1:
		value = value / 1024.0
		unit_id += 1
	return float_to_str(value, max_decimals=2) + BYTE_UNITS[unit_id]

def create_temp_file(name: str, createmode: int | None = None) -> str:
	directory, filename = os.path.split(name)
	handle, temp_file = tempfile.mkstemp(prefix=f".{filename}-", dir=directory)
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
		# Fire-and-forget launch of the system file viewer; we intentionally do not wait for it.
		subprocess.Popen([cmd, filepath])  # pylint: disable=consider-using-with

play_sound: Callable[[bytes], None] | None = None
try:
	from winsound import PlaySound, SND_MEMORY # type: ignore[attr-defined] # pylint: disable=import-error
	def win_play(raw_audio):
		start_new_thread(PlaySound, (raw_audio, SND_MEMORY))
	play_sound = win_play
except Exception:
	def osx_play(raw_audio):
		from . import Assets  # pylint: disable=cyclic-import
		def do_play(path):
			try:
				subprocess.call(["afplay", path])
			except Exception:
				pass
			try:
				os.remove(path)
			except Exception:
				pass
		temp_file = create_temp_file(Assets.internal_temp_file_path())
		with open(temp_file, 'wb') as handle:
			handle.write(raw_audio)
			handle.flush()
			os.fsync(handle.fileno())
		start_new_thread(do_play, (temp_file,))
	play_sound = osx_play
