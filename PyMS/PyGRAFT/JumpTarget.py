from __future__ import annotations

from ..FileFormats.Graft.CodeHandlers import ButtonCodeCommands, RequirementCodeCommands
from ..FileFormats.Graft.CodeHandlers.GraftCommandDefinition import GraftCommandDefinition
from ..FileFormats.Graft.CodeHandlers.RequirementCodeCommands import ReqCommandDefinition

from enum import Enum

# What a Jump To button (or a Used By row) jumps to: an entry of one of the main window's tabs
class JumpTarget(Enum):
	button_sets = 'Button Set'
	button_cards = 'Button Card'
	unit_reqs = 'Unit Training Reqs.'
	upgrade_reqs = 'Upgrade Research Reqs.'
	research_reqs = 'Tech Research Reqs.'
	tech_reqs = 'Tech Usage Reqs.'

	@property
	def tooltip(self) -> str:
		return f'Jump To {self.value}'

	@classmethod
	def for_button_function(cls, cmd_def: GraftCommandDefinition) -> JumpTarget | None:
		# What a button condition's or action's parameter jumps to (`None` when it has no parameter, or its parameter is unused or isn't a reference)
		return _BUTTON_FUNCTION_TARGETS.get(cmd_def)

	@classmethod
	def for_req_command(cls, cmd_def: ReqCommandDefinition) -> JumpTarget | None:
		# What a requirement opcode's parameter jumps to (`None` when it has no parameter)
		return _REQ_COMMAND_TARGETS.get(cmd_def)

_BUTTON_FUNCTION_TARGETS: dict[GraftCommandDefinition, JumpTarget] = {
	# Conditions
	ButtonCodeCommands.CanCreateOrMorph: JumpTarget.unit_reqs,
	ButtonCodeCommands.CanBuildSubunit: JumpTarget.unit_reqs,
	ButtonCodeCommands.CanCreateSingle: JumpTarget.unit_reqs,
	ButtonCodeCommands.CanResearchTech: JumpTarget.research_reqs,
	ButtonCodeCommands.CanPlayerUseTech: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanUnitsUseTech: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanCloak: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanDecloak: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanSiege: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanUnsiege: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanBurrow: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanUnburrow: JumpTarget.tech_reqs,
	ButtonCodeCommands.IsTechUnusable: JumpTarget.tech_reqs,
	ButtonCodeCommands.IsTechUnusableB: JumpTarget.tech_reqs,
	ButtonCodeCommands.CanUpgrade: JumpTarget.upgrade_reqs,
	# Actions
	ButtonCodeCommands.Train: JumpTarget.unit_reqs,
	ButtonCodeCommands.BuildTerran: JumpTarget.unit_reqs,
	ButtonCodeCommands.BuildProtoss: JumpTarget.unit_reqs,
	ButtonCodeCommands.BuildAddon: JumpTarget.unit_reqs,
	ButtonCodeCommands.BuildZerg: JumpTarget.unit_reqs,
	ButtonCodeCommands.PlaceNydusExit: JumpTarget.unit_reqs,
	ButtonCodeCommands.MorphBuilding: JumpTarget.unit_reqs,
	ButtonCodeCommands.MorphUnit: JumpTarget.unit_reqs,
	ButtonCodeCommands.Land: JumpTarget.unit_reqs,
	ButtonCodeCommands.ResearchTech: JumpTarget.research_reqs,
	ButtonCodeCommands.UseTech: JumpTarget.tech_reqs,
	ButtonCodeCommands.Upgrade: JumpTarget.upgrade_reqs,
	ButtonCodeCommands.ShowButtonCard: JumpTarget.button_cards,
}

_REQ_COMMAND_TARGETS: dict[ReqCommandDefinition, JumpTarget] = {
	RequirementCodeCommands.CurrentUnitIs: JumpTarget.unit_reqs,
	RequirementCodeCommands.MustHave: JumpTarget.unit_reqs,
	RequirementCodeCommands.MustHaveAddon: JumpTarget.unit_reqs,
	RequirementCodeCommands.HasCompleted: JumpTarget.unit_reqs,
	RequirementCodeCommands.IsResearched: JumpTarget.research_reqs,
}
