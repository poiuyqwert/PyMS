
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, RawActionDefinition
from .Parameters import *
from .Action import Action
from .Constants import BriefingActionType, Matches

action_definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition('NoAction', BriefingActionType.no_action),
    BasicActionDefinition('Wait', BriefingActionType.wait, (TimeParameter(),)),
    BasicActionDefinition('PlayWAV', BriefingActionType.play_wav, (WAVParameter(), TimeParameter())),
    BasicActionDefinition('DisplayTextMessage', BriefingActionType.text_message, (StringParameter(), TimeParameter())),
    BasicActionDefinition('SetMissionObjectives', ActionType.set_mission_objectives, (StringParameter(),)),
    BasicActionDefinition('ShowPortrait', BriefingActionType.show_portrait, (UnitParameter(), SlotParameter())),
    BasicActionDefinition('HidePortrait', BriefingActionType.hide_portrait, (SlotParameter(),)),
    BasicActionDefinition('DisplaySpeakingPortrait', BriefingActionType.display_speaking_portrait, (SlotParameter(), TimeParameter())),
    BasicActionDefinition('Transmission', BriefingActionType.transmission, (StringParameter(), SlotParameter(), WAVParameter(), TimeParameter(wav=True), ModifierParameter(), TimeParameter())),
	BasicActionDefinition('SkipTutorialEnabled', BriefingActionType.skip_tutorial_enabled),

	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	action_definitions_registry.append(definition)

def get_definition(condition: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in action_definitions_registry:
		matches = definition.matches(condition)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_action_named(name: str) -> (ActionDefinition | None):
	for definition in action_definitions_registry:
		if definition.name == name:
			return definition
	return None
