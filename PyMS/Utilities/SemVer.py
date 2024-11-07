
from typing import Any

class SemVer(object):
	def __init__(self, version: str) -> None:
		self.meta = None
		if '-' in version:
			version,self.meta = version.split('-')
		components = (int(c) for c in version.split('.'))
		self.major, self.minor, self.patch = components

	def __lt__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return False
		if self.major < other.major:
			return True
		elif self.major > other.major:
			return False
		if self.minor < other.minor:
			return True
		elif self.minor > other.minor:
			return False
		if self.patch < other.patch:
			return True
		elif self.patch > other.patch:
			return False
		return False

	def __gt__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return False
		if self.major > other.major:
			return True
		elif self.major < other.major:
			return False
		if self.minor > other.minor:
			return True
		elif self.minor < other.minor:
			return False
		if self.patch > other.patch:
			return True
		elif self.patch < other.patch:
			return False
		return False

	def __eq__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return False
		if self.major != other.major:
			return False
		if self.minor != other.minor:
			return False
		if self.patch != other.patch:
			return False
		return True

	def __ge__(self, other: Any) -> bool:
		return self.__gt__(other) or self.__eq__(other)

	def __repr__(self) -> str:
		meta = f'-{self.meta}' if self.meta else ''
		return f'<SemVer {self.major}.{self.minor}.{self.patch}{meta}>'
