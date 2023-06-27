
from __future__ import annotations

import os, io, tempfile

from typing import IO, Callable, TypeAlias

AnyInputText = str | IO[str]
AnyInputBytes = str | bytes | IO[bytes]

AnyOutputText = str | IO[str]
AnyOutputBytes = str | IO[bytes]

class InputText:
	def __init__(self, input: AnyInputText):
		self.entered = 0
		self.close = False
		self.file: IO[str]
		if isinstance(input, str):
			if os.path.exists(input):
				self.file = open(input, 'r')
				self.close = True
			else:
				self.file = io.StringIO(input)
		else:
			self.file = input

	def __enter__(self) -> IO[str]:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()

class InputBytes:
	def __init__(self, input: AnyInputBytes):
		self.entered = 0
		self.close = False
		self.file: IO[bytes]
		if isinstance(input, str):
			self.file = open(input, 'rb')
			self.close = True
		elif isinstance(input, bytes):
			self.file = io.BytesIO(input)
		else:
			self.file = input

	def __enter__(self) -> IO[bytes]:
		self.entered += 1
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		self.entered -= 1
		if self.entered == 0 and self.close:
			self.file.close()

class OutputText:
	def __init__(self, output: AnyOutputText):
		self.close = False
		self.file: IO[str]
		self.atomic_paths: tuple[str, str] | None = None
		if isinstance(output, str):
			directory, filename = os.path.split(os.path.abspath(output))
			temp_file = tempfile.NamedTemporaryFile('w', prefix=f'.{filename}-', dir=directory, delete=False)
			self.file = temp_file
			self.atomic_paths = (temp_file.name, output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> IO[str]:
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		if self.close:
			self.file.close()
		if self.atomic_paths is not None:
			temp_path, final_path = self.atomic_paths
			os.rename(temp_path, final_path)

class OutputBytes:
	def __init__(self, output: AnyOutputBytes):
		self.close = False
		self.file: IO[bytes]
		self.atomic_paths: tuple[str, str] | None = None
		if isinstance(output, str):
			directory, filename = os.path.split(os.path.abspath(output))
			temp_file = tempfile.NamedTemporaryFile('wb', prefix=f'.{filename}-', dir=directory, delete=False)
			self.file = temp_file
			self.atomic_paths = (temp_file.name, output)
			self.close = True
		else:
			self.file = output

	def __enter__(self) -> IO[bytes]:
		return self.file

	def __exit__(self, exc_type, exc_value, traceback):
		if self.close:
			self.file.close()
		if self.atomic_paths is not None:
			temp_path, final_path = self.atomic_paths
			os.rename(temp_path, final_path)

def output_to_text(func: Callable[[IO[str]], None]) -> str:
	output = io.StringIO()
	func(output)
	return output.getvalue()

def output_to_bytes(func: Callable[[IO[bytes]], None]) -> bytes:
	output = io.BytesIO()
	func(output)
	return output.getvalue()
