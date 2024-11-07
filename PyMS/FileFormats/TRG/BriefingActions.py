
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, RawActionDefinition
from .Parameters import *
from .Action import Action
from .Constants import BriefingActionType, Matches

definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition('NoAction', 'No action', BriefingActionType.no_action),
    BasicActionDefinition('Wait', 'Wait for {1} milliseconds.', BriefingActionType.wait, (TimeParameter(),)),
    BasicActionDefinition('PlayWAV', 'Play {0} with duration {2}.', BriefingActionType.play_wav, (WAVParameter(), TimeParameter())),
    BasicActionDefinition('DisplayTextMessage', 'Display {0} for current player when {1}.', BriefingActionType.text_message, (StringParameter(), TimeParameter())),
    BasicActionDefinition('SetMissionObjectives', 'Set mission objectives to {0}.', ActionType.set_mission_objectives, (StringParameter(),)),
    BasicActionDefinition('ShowPortrait', 'Show portrait of {0} in {1}.', BriefingActionType.show_portrait, (UnitParameter(), SlotParameter())),
    BasicActionDefinition('HidePortrait', 'Hide portrait in {1}.', BriefingActionType.hide_portrait, (SlotParameter(),)),
    BasicActionDefinition('DisplaySpeakingPortrait', 'Display speaking portrait in {0} for {1} milliseconds.', BriefingActionType.display_speaking_portrait, (SlotParameter(), TimeParameter())),
    BasicActionDefinition('Transmission', 'Send transmission to current player for {1}. Play {2} with duration {3}. Modify transmission duration: {4} {5} milliseconds. Display {0}.', BriefingActionType.transmission, (StringParameter(), SlotParameter(), WAVParameter(), TimeParameter(), ModifierParameter(), TimeParameter(transmission=True))),
	BasicActionDefinition('SkipTutorialEnabled', 'Show the Skip Tutorial button in the briefing UI.', BriefingActionType.skip_tutorial_enabled),

	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	definitions_registry.append(definition)

def get_definition(action: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in definitions_registry:
		matches = definition.matches(action)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_definition_named(name: str) -> (ActionDefinition | None):
	for definition in definitions_registry:
		if definition.name == name:
			return definition
	return None
