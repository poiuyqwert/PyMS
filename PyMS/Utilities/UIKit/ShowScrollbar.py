
from enum import Enum

__all__ = [
	'ShowScrollbar',
]

class ShowScrollbar(Enum):
	never = 0
	always = 1
	when_needed = 2
