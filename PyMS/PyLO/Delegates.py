
from ..Utilities import UIKit as UI

from typing import Protocol

class FindDelegate(Protocol):
	def get_text(self) -> UI.CodeText:
		...
