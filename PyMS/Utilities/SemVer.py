
from typing import Any

class SemVer:
	def __init__(self, version: str) -> None:
		self.meta = None
		if '-' in version:
			version,self.meta = version.split('-', 1)
		parts = version.split('.')
		if len(parts) != 3:
			raise ValueError(f"Invalid SemVer '{version}': expected 'major.minor.patch'")
		self.major, self.minor, self.patch = (int(c) for c in parts)

	def __lt__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return False
		if self.major < other.major:
			return True
		if self.major > other.major:
			return False
		if self.minor < other.minor:
			return True
		if self.minor > other.minor:
			return False
		if self.patch < other.patch:
			return True
		if self.patch > other.patch:
			return False
		return False

	def __gt__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return False
		if self.major > other.major:
			return True
		if self.major < other.major:
			return False
		if self.minor > other.minor:
			return True
		if self.minor < other.minor:
			return False
		if self.patch > other.patch:
			return True
		if self.patch < other.patch:
			return False
		return False

	def __eq__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return NotImplemented
		if self.major != other.major:
			return False
		if self.minor != other.minor:
			return False
		if self.patch != other.patch:
			return False
		return True

	def __ge__(self, other: Any) -> bool:
		if not isinstance(other, SemVer):
			return NotImplemented
		return self.__gt__(other) or self.__eq__(other)

	def __repr__(self) -> str:
		meta = f'-{self.meta}' if self.meta else ''
		return f'<SemVer {self.major}.{self.minor}.{self.patch}{meta}>'
