
from .ICEHeaderSourceCodeParser import ICEHeaderSourceCodeParser
from .ICEBlockSourceCodeParser import ICEBlockSourceCodeParser

from ....Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler
from ....Utilities.CodeHandlers.SourceCodeParser import CommandSourceCodeParser

class ICESourceCodeHandler(SourceCodeHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_parser(ICEHeaderSourceCodeParser())
		self.register_parser(ICEBlockSourceCodeParser())
		self.register_parser(CommandSourceCodeParser())
