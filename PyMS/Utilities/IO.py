
from __future__ import annotations

import os, io, tempfile

from typing import IO, Callable, Iterable, Iterator, Any, Literal

AnyInputText = str | IO[str]
AnyInputBytes = str | bytes | IO[bytes]

AnyOutputText = str | IO[str]
AnyOutputBytes = str | IO[bytes]

class IOException(Exception):
	pass

class InputText:
	def __init__(self, any_input: AnyInputText):
		self.entered = 0
		self.close = False
		self.file: IO[str]
		if isinstance(any_input, str):
			if os.path.exists(any_input):
				self.file = open(any_input, 'r', encoding='utf-8')
				self.close = True
			else:
				self.file = io.StringIO(any_input)
		else:
			self.file = any_input

	def __enter__(self) -> IO[str]:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()
			self.close = False
		return False

class InputBytes:
	def __init__(self, any_input: AnyInputBytes):
		self.entered = 0
		self.close = False
		self.file: IO[bytes]
		if isinstance(any_input, str):
			self.file = open(any_input, 'rb')
			self.close = True
		elif isinstance(any_input, bytes):
			self.file = io.BytesIO(any_input)
		else:
			self.file = any_input

	def __enter__(self) -> IO[bytes]:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()
			self.close = False
		return False

class OutputTextFile(IO[str]):
	def __init__(self, path: str, encoding: str = 'utf-8') -> None:
		self.path = path
		directory, filename = os.path.split(os.path.abspath(path))
		self.temp_file = tempfile.NamedTemporaryFile('w', prefix=f'.{filename}-', dir=directory, delete=False, encoding=encoding)

	@property
	def mode(self) -> str:
		return self.temp_file.mode

	@property
	def name(self) -> str:
		return self.temp_file.name

	def close(self) -> None:
		if self.closed:
			return
		self.temp_file.close()
		os.replace(self.temp_file.name, self.path)

	@property
	def closed(self) -> bool:
		return self.temp_file.closed

	def fileno(self) -> int:
		return self.temp_file.fileno()

	def flush(self) -> None:
		self.temp_file.flush()

	def isatty(self) -> bool:
		return self.temp_file.isatty()

	def read(self, n: int = -1) -> str:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def readable(self) -> bool:
		return False

	def readline(self, limit: int = -1) -> str:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def readlines(self, hint: int = -1) -> list[str]:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def seek(self, offset: int, whence: int = 0) -> int:
		raise IOException(f'Attempting to seek in {self.__class__.__name__}')

	def seekable(self) -> bool:
		return False

	def tell(self) -> int:
		raise IOException(f'Attempting to tell in {self.__class__.__name__}')

	def truncate(self, size: int | None = None) -> int:
		raise IOException(f'Attempting to truncate in {self.__class__.__name__}')

	def writable(self) -> bool:
		return self.temp_file.writable()

	def write(self, s: str) -> int:
		return self.temp_file.write(s)

	def writelines(self, lines: Iterable[str]) -> None:
		self.temp_file.writelines(lines)

	def __enter__(self) -> IO[str]:
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
		self.close()

	def __iter__(self) -> Iterator[str]:
		raise IOException(f'Attempting to iterate a {self.__class__.__name__}')

	def __next__(self) -> str:
		raise IOException(f'Attempting to next a {self.__class__.__name__}')

class OutputBytesFile(IO[bytes]):
	def __init__(self, path: str) -> None:
		self.path = path
		directory, filename = os.path.split(os.path.abspath(path))
		self.temp_file = tempfile.NamedTemporaryFile('wb', prefix=f'.{filename}-', dir=directory, delete=False)

	@property
	def mode(self) -> str:
		return self.temp_file.mode

	@property
	def name(self) -> str:
		return self.temp_file.name

	def close(self) -> None:
		if self.closed:
			return
		self.temp_file.close()
		os.replace(self.temp_file.name, self.path)

	@property
	def closed(self) -> bool:
		return self.temp_file.closed

	def fileno(self) -> int:
		return self.temp_file.fileno()

	def flush(self) -> None:
		self.temp_file.flush()

	def isatty(self) -> bool:
		return self.temp_file.isatty()

	def read(self, n: int = -1) -> bytes:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def readable(self) -> bool:
		return False

	def readline(self, limit: int = -1) -> bytes:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def readlines(self, hint: int = -1) -> list[bytes]:
		raise IOException(f'Attempting to read from {self.__class__.__name__}')

	def seek(self, offset: int, whence: int = 0) -> int:
		raise IOException(f'Attempting to seek in {self.__class__.__name__}')

	def seekable(self) -> bool:
		return False

	def tell(self) -> int:
		raise IOException(f'Attempting to tell in {self.__class__.__name__}')

	def truncate(self, size: int | None = None) -> int:
		raise IOException(f'Attempting to truncate in {self.__class__.__name__}')

	def writable(self) -> bool:
		return self.temp_file.writable()

	def write(self, b: bytes | bytearray) -> int: # type: ignore[override]
		return self.temp_file.write(b)

	def writelines(self, lines: Iterable[bytes | bytearray]) -> None: # type: ignore[override]
		self.temp_file.writelines(lines)

	def __enter__(self) -> IO[bytes]:
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
		self.close()

	def __iter__(self) -> Iterator[bytes]:
		raise IOException(f'Attempting to iterate a {self.__class__.__name__}')

	def __next__(self) -> bytes:
		raise IOException(f'Attempting to next a {self.__class__.__name__}')

class OutputText:
	def __init__(self, output: AnyOutputText):
		self.close = False
		self.file: IO[str]
		if isinstance(output, str):
			self.file = OutputTextFile(output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> IO[str]:
		return self.file

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
		if self.close:
			self.file.close()
			self.close = False
		return False

class OutputBytes:
	def __init__(self, output: AnyOutputBytes):
		self.close = False
		self.file: IO[bytes]
		if isinstance(output, str):
			self.file = OutputBytesFile(output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> IO[bytes]:
		return self.file

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Literal[False]:
		if self.close:
			self.file.close()
			self.close = False
		return False

def open_input_text(any_input: AnyInputText) -> IO[str]:
	if isinstance(any_input, str):
		if os.path.exists(any_input):
			return open(any_input, 'r', encoding='utf-8')
		else:
			return io.StringIO(any_input)
	else:
		return any_input

def open_input_bytes(any_input: AnyInputBytes) -> IO[bytes]:
	if isinstance(any_input, str):
		return open(any_input, 'rb')
	elif isinstance(any_input, bytes):
		return io.BytesIO(any_input)
	else:
		return any_input

def open_output_text(output: AnyOutputText) -> IO[str]:
	if isinstance(output, str):
		return OutputTextFile(output)
	else:
		return output

def open_output_bytes(output: AnyOutputBytes) -> IO[bytes]:
	if isinstance(output, str):
		return OutputBytesFile(output)
	else:
		return output

def output_to_text(func: Callable[[IO[str]], None]) -> str:
	output = io.StringIO()
	func(output)
	return output.getvalue()

def output_to_bytes(func: Callable[[IO[bytes]], None]) -> bytes:
	output = io.BytesIO()
	func(output)
	return output.getvalue()
