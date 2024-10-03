
from __future__ import annotations

import os, io, tempfile

from typing import TextIO, BinaryIO, Callable, Iterable, Iterator

AnyInputText = str | TextIO
AnyInputBytes = str | bytes | BinaryIO

AnyOutputText = str | TextIO
AnyOutputBytes = str | BinaryIO

class InputText:
	def __init__(self, input: AnyInputText):
		self.entered = 0
		self.close = False
		self.file: TextIO
		if isinstance(input, str):
			if os.path.exists(input):
				self.file = open(input, 'r')
				self.close = True
			else:
				self.file = io.StringIO(input)
		else:
			self.file = input

	def __enter__(self) -> TextIO:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()
			self.close = False

class InputBytes:
	def __init__(self, input: AnyInputBytes):
		self.entered = 0
		self.close = False
		self.file: BinaryIO
		if isinstance(input, str):
			self.file = open(input, 'rb')
			self.close = True
		elif isinstance(input, bytes):
			self.file = io.BytesIO(input)
		else:
			self.file = input

	def __enter__(self) -> BinaryIO:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()
			self.close = False

class OutputTextFile(TextIO):
	def __init__(self, path: str) -> None:
		self.path = path
		directory, filename = os.path.split(os.path.abspath(path))
		self.temp_file = tempfile.NamedTemporaryFile('w', prefix=f'.{filename}-', dir=directory, delete=False)

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
		os.rename(self.temp_file.name, self.path)

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
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def readable(self) -> bool:
		return False

	def readline(self, limit: int = -1) -> str:
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def readlines(self, hint: int = -1) -> list[str]:
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def seek(self, offset: int, whence: int = 0) -> int:
		raise Exception(f'Attempting to seek in {self.__class__.__name__}')

	def seekable(self) -> bool:
		return False

	def tell(self) -> int:
		raise Exception(f'Attempting to tell in {self.__class__.__name__}')

	def truncate(self, size: int | None = None) -> int:
		raise Exception(f'Attempting to truncate in {self.__class__.__name__}')

	def writable(self) -> bool:
		return self.temp_file.writable()

	def write(self, s: str) -> int:
		return self.temp_file.write(s)

	def writelines(self, lines: Iterable[str]) -> None:
		self.temp_file.writelines(lines)

	def __enter__(self) -> TextIO:
		return self

	def __exit__(self, type, value, traceback) -> None:
		self.close()

	def __iter__(self) -> Iterator[str]:
		raise Exception(f'Attempting to iterate a {self.__class__.__name__}')
	
	def __next__(self) -> str:
		raise Exception(f'Attempting to next a {self.__class__.__name__}')

class OutputBytesFile(BinaryIO):
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
		os.rename(self.temp_file.name, self.path)

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
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def readable(self) -> bool:
		return False

	def readline(self, limit: int = -1) -> bytes:
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def readlines(self, hint: int = -1) -> list[bytes]:
		raise Exception(f'Attempting to read from {self.__class__.__name__}')

	def seek(self, offset: int, whence: int = 0) -> int:
		raise Exception(f'Attempting to seek in {self.__class__.__name__}')

	def seekable(self) -> bool:
		return False

	def tell(self) -> int:
		raise Exception(f'Attempting to tell in {self.__class__.__name__}')

	def truncate(self, size: int | None = None) -> int:
		raise Exception(f'Attempting to truncate in {self.__class__.__name__}')

	def writable(self) -> bool:
		return self.temp_file.writable()

	def write(self, b: bytes | bytearray) -> int: # type: ignore[override]
		return self.temp_file.write(b)

	def writelines(self, lines: Iterable[bytes | bytearray]) -> None: # type: ignore[override]
		self.temp_file.writelines(lines)

	def __enter__(self) -> BinaryIO:
		return self

	def __exit__(self, type, value, traceback) -> None:
		self.close()

	def __iter__(self) -> Iterator[bytes]:
		raise Exception(f'Attempting to iterate a {self.__class__.__name__}')
	
	def __next__(self) -> bytes:
		raise Exception(f'Attempting to next a {self.__class__.__name__}')

class OutputText:
	def __init__(self, output: AnyOutputText):
		self.close = False
		self.file: TextIO
		if isinstance(output, str):
			self.file = OutputTextFile(output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> TextIO:
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		if self.close:
			self.file.close()
			self.close = False

class OutputBytes:
	def __init__(self, output: AnyOutputBytes):
		self.close = False
		self.file: BinaryIO
		if isinstance(output, str):
			self.file = OutputBytesFile(output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> BinaryIO:
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		if self.close:
			self.file.close()
			self.close = False

def open_input_text(input: AnyInputText) -> TextIO:
	if isinstance(input, str):
		if os.path.exists(input):
			return open(input, 'r')
		else:
			return io.StringIO(input)
	else:
		return input

def open_input_bytes(input: AnyInputBytes) -> BinaryIO:
	if isinstance(input, str):
		return open(input, 'rb')
	elif isinstance(input, bytes):
		return io.BytesIO(input)
	else:
		return input

def open_output_text(output: AnyOutputText) -> TextIO:
	if isinstance(output, str):
		return OutputTextFile(output)
	else:
		return output

def open_output_bytes(output: AnyOutputBytes) -> BinaryIO:
	if isinstance(output, str):
		return OutputBytesFile(output)
	else:
		return output

def output_to_text(func: Callable[[TextIO], None]) -> str:
	output = io.StringIO()
	func(output)
	return output.getvalue()

def output_to_bytes(func: Callable[[BinaryIO], None]) -> bytes:
	output = io.BytesIO()
	func(output)
	return output.getvalue()
