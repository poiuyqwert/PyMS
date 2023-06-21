
from enum import Enum

class CheckSaved(Enum):
	cancelled = 0
	saved = 1 # Also covers not open, not edited, and chose to ignore changes
