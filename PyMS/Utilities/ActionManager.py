
from typing import Protocol

from .Callback import Callback

class Action(Protocol):
	def has_changes(self) -> bool:
		return False

	def apply(self) -> None:
		...

	def undo(self) -> None:
		...

class ActionGroup(Action):
	def __init__(self) -> None:
		self.actions: list[Action] = []
		self.complete = False

	def add_action(self, action: Action, apply: bool = True) -> None:
		group: ActionGroup | None = None
		if self.actions:
			last_action = self.actions[-1]
			if isinstance(last_action, ActionGroup):
				group = last_action
		if group and not group.complete:
			group.add_action(action)
		else:
			self.actions.append(action)
		if apply:
			action.apply()

	def remove_action(self, action: Action, undo: bool = False) -> None:
		self.actions.remove(action)
		if undo:
			action.undo()

	def has_changes(self) -> bool:
		for action in self.actions:
			if action.has_changes():
				return True
		return False

	def apply(self) -> None:
		for action in self.actions:
			action.apply()

	def undo(self) -> None:
		for action in reversed(self.actions):
			action.undo()

class ActionManager(ActionGroup):
	def __init__(self) -> None:
		ActionGroup.__init__(self)
		self.redos: list[Action] = []
		self.state_updated: Callback[[]] = Callback()

	def get_open_group(self) -> tuple[ActionGroup, ActionGroup]:
		parent: ActionGroup = self
		group: ActionGroup = self
		while group.actions:
			action = group.actions[-1]
			if not isinstance(action, ActionGroup):
				break
			if not action.complete:
				break
			parent = group
			group = action
		return (parent, group)

	def start_group(self) -> None:
		self.add_action(ActionGroup())

	def end_group(self) -> None:
		parent,open_group = self.get_open_group()
		if open_group == self:
			return
		open_group.complete = True
		if not open_group.has_changes():
			parent.remove_action(open_group)
		elif len(open_group.actions) == 1:
			parent.add_action(open_group.actions[0])
			parent.remove_action(open_group)

	def add_action(self, action: Action, apply: bool = True) -> None:
		self.redos.clear()
		ActionGroup.add_action(self, action, apply)
		self.state_updated()

	def can_undo(self) -> bool:
		return (len(self.actions) > 0)

	def undo(self) -> None:
		if not self.can_undo():
			return
		action = self.actions[-1]
		self.redos.append(action)
		del self.actions[-1]
		action.undo()
		self.state_updated()

	def can_redo(self) -> bool:
		return (len(self.redos) > 0)

	def redo(self) -> None:
		if not self.can_redo():
			return
		action = self.redos[-1]
		self.actions.append(action)
		del self.redos[-1]
		action.apply()
		self.state_updated()

	def clear(self) -> None:
		self.actions.clear()
		self.redos.clear()
		self.state_updated()
