
import copy

class Action:
	def __init__(self):
		pass

	def has_changes(self):
		return False

	def update_display(self, info=None):
		pass

	def undo(self):
		pass

	def redo(self):
		pass

class ActionUpdateValues(Action):
	def __init__(self, obj, attrs):
		Action.__init__(self)
		self.start_values = {}
		for attr in attrs:
			if hasattr(obj, attr):
				self.start_values[attr] = copy.deepcopy(getattr(obj, attr))
		self.end_values = None

	def set_end_values(self, obj, attrs):
		self.end_values = {}
		for attr in attrs:
			if hasattr(obj, attr):
				self.end_values[attr] = copy.deepcopy(getattr(obj, attr))

	def has_changes(self):
		return (self.start_values != self.end_values)

	def get_obj(self):
		return None

	def apply_values(self, obj, from_values, to_values):
		from_attrs = set(from_values.keys())
		to_attrs = set(to_values.keys())
		del_attrs = from_attrs - to_attrs
		for attr in del_attrs:
			delattr(obj, attr)
		for name in to_attrs:
			setattr(obj, name, copy.deepcopy(to_values[name]))

	def undo(self):
		self.apply_values(self.get_obj(), self.end_values, self.start_values)
		self.update_display(self.start_values)

	def redo(self):
		self.apply_values(self.get_obj(), self.start_values, self.end_values)
		self.update_display(self.end_values)

class ActionUpdateArray(Action):
	def __init__(self):
		self.start_values = []
		self.end_values = []

	def update_values(self, obj, indices, values):
		for indexes,v in zip(indices,values):
			array = obj
			i = 0
			while len(indexes) - i:
				array = array[indexes[i]]
				i += 1
			self.start_values.append((indexes, array[indexes[i]]))
			self.end_values.append((indexes, v))

	def update_value(self, obj, indices, value):
		self.update_values(obj, indices, (value,) * len(indices))

	def has_changes(self):
		return (self.start_values != self.end_values)

	def apply_values(self, obj, values):
		for indexes,v in values:
			array = arrays
			i = 0
			while len(indexes) - i:
				array = array[indexes[i]]
				i += 1
			array[indexes[i]] = v

	def get_obj(self):
		return None

	def undo(self):
		self.apply_values(self.get_obj(), self.start_values)
		self.update_display(self.start_values)

	def redo(self):
		self.apply_values(self.get_obj(), self.end_values)
		self.update_display(self.end_values)

class ActionGroup(Action):
	def __init__(self):
		self.actions = []
		self.complete = False

	def add_action(self, action):
		group = None
		if self.actions:
			group = self.actions[-1]
		if isinstance(group, ActionGroup) and not group.complete:
			group.add_action(action)
		else:
			self.actions.append(action)

	def remove_action(self, action):
		self.actions.remove(action)

	def has_changes(self):
		for action in self.actions:
			if action.has_changes():
				return True
		return False

	def undo(self):
		for action in reversed(self.actions):
			action.undo()

	def redo(self):
		for action in self.actions:
			action.redo()

class ActionManager(ActionGroup):
	def __init__(self):
		ActionGroup.__init__(self)
		self.redos = []

	def get_open_group(self):
		parent,group = self,self
		while isinstance(group, ActionGroup) and group.actions and isinstance(group.actions[-1], ActionGroup) and not group.actions[-1].complete:
			parent = group
			group = group.actions[-1]
		return (parent,group)

	def start_group(self):
		self.add_action(ActionGroup())

	def end_group(self):
		parent,open_group = self.get_open_group()
		if open_group != self:
			open_group.complete = True
			if not open_group.has_changes():
				parent.remove_action(open_group)
			elif len(open_group.actions) == 1:
				parent.add_action(open_group.actions[0])
				parent.remove_action(open_group)

	def add_action(self, action):
		self.redos = []
		ActionGroup.add_action(self, action)

	def can_undo(self):
		return (len(self.actions) > 0)

	def undo(self):
		if self.can_undo():
			action = self.actions[-1]
			self.redos.append(action)
			del self.actions[-1]
			action.undo()

	def can_redo(self):
		return (len(self.redos) > 0)

	def redo(self):
		if self.can_redo():
			action = self.redos[-1]
			self.actions.append(action)
			del self.redos[-1]
			action.redo()
