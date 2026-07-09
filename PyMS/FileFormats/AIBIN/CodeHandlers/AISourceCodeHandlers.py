
from .AIHeaderSourceCodeParser import AIHeaderSourceCodeParser
from . import CodeDirectives

from ....Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler
from ....Utilities.CodeHandlers.SourceCodeParser import BlockSourceCodeParser, CommandSourceCodeParser, DirectiveSourceCodeParser, DefineSourceCodeParser

class AISourceCodeHandler(SourceCodeHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_parser(AIHeaderSourceCodeParser())
		self.register_parser(BlockSourceCodeParser())
		self.register_parser(CommandSourceCodeParser())
		self.register_parser(DirectiveSourceCodeParser(CodeDirectives.all_basic_directives + CodeDirectives.all_defs_directives))
		self.register_parser(DefineSourceCodeParser())

class AIDefsSourceCodeHandler(SourceCodeHandler):
	def __init__(self) -> None:
		super().__init__()
		self.register_parser(DefineSourceCodeParser())
		self.register_parser(DirectiveSourceCodeParser(CodeDirectives.all_defs_directives))
