
from __future__ import annotations

from .AILanguage import AILanguage
from . import CodeDirectives
from .DataContext import DataContext

from ....Utilities.CodeHandlers.ParseContext import ParseContext, ParseSettings
from ....Utilities.CodeHandlers.Lexer import Lexer
from ....Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ....Utilities.CodeHandlers.CodeDirective import CodeDirective
from ....Utilities.PyMSError import PyMSError

from collections import OrderedDict

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..AIScript import AIScript

class AIParseSettings(ParseSettings):
	def __init__(self) -> None:
		super().__init__()
		self.expanded_units: int | None = None
		self.expanded_upgrades: int | None = None
		self.expanded_tech: int | None = None

class AIParseContext(ParseContext[AIParseSettings]):
	def __init__(self, lexer: Lexer, settings: AIParseSettings, definitions: DefinitionsHandler, data_context: DataContext) -> None:
		ParseContext.__init__(self, lexer, AILanguage(), settings, definitions)
		self.data_context = data_context
		self.spellcasters: list[int] = []
		self.scripts: OrderedDict[str, tuple[AIScript, int]] = OrderedDict()

	def handle_directive(self, directive: CodeDirective) -> None:
		if directive.definition == CodeDirectives.Spellcaster:
			assert self.definitions is not None
			variable = self.definitions.get_variable(directive.params[0])
			assert variable is not None
			self.spellcasters.append(variable.value)
		elif directive.definition == CodeDirectives.SupressAll:
			self.add_supressed_warning_id(directive.params[0])
		elif directive.definition == CodeDirectives.SupressNextLine:
			self.add_supressed_warning_id(directive.params[0], True)
		elif directive.definition == CodeDirectives.ExpandUnits:
			self.settings.expanded_units = max(self.settings.expanded_units or 0, directive.params[0])
		elif directive.definition == CodeDirectives.ExpandUpgrades:
			self.settings.expanded_upgrades = max(self.settings.expanded_upgrades or 0, directive.params[0])
		elif directive.definition == CodeDirectives.ExpandTech:
			self.settings.expanded_tech = max(self.settings.expanded_tech or 0, directive.params[0])

	def finalize(self) -> None:
		from ..AIScript import AIScript
		for block_metadata in self.block_metadata.values():
			if not block_metadata.uses:
				# TODO: Should have warning here?
				continue
			uses = cast(list[AIScript], block_metadata.uses)
			aiscripts = list(script.id for script in uses if not script.in_bwscript)
			bwscripts = list(script.id for script in uses if script.in_bwscript)
			if aiscripts and bwscripts:
				raise PyMSError('Parse', f"Block '{block_metadata.name}' is cross referenced by scripts in aiscript.bin ({', '.join(aiscripts)}) and bwscript.bin ({', '.join(bwscripts)})")
		# TODO: Check for loops without waits
		# TODO: Check for other issues with scripts
		return super().finalize()
