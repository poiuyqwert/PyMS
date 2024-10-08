
from ..Widgets import *
from ..Font import Font
from ... import Assets
from ..EventPattern import *
from ..Types import SelectMode

import re
from enum import Enum

from typing import Callable, Sequence

class SelectModifier(Enum):
	none = 0
	shift = 1
	ctrl = 2

class TreeNode:
	def __init__(self, text: str, depth: int, entry: int) -> None:
		self.text = text
		self.depth = depth
		self.entry = entry
		self.parent: TreeGroup | None = None

	def __repr__(self) -> str:
		return '<TreeNode text=%s depth=%d entry=%d>' % (repr(self.text), self.depth, self.entry)

class TreeGroup(TreeNode):
	def __init__(self, text: str, depth: int, entry: int, expanded: bool) -> None:
		TreeNode.__init__(self, text, depth, entry)
		self.entry = entry
		self.expanded = expanded
		self.children: list[TreeNode] = []

	def add_child(self, child: TreeNode) -> None:
		self.children.append(child)
		child.parent = self

	def __repr__(self) -> str:
		children = ''
		for child in self.children:
			children += '\n\t' + repr(child).replace('\n','\n\t')
		if children:
			children += '\n'
		return '<TreeGroup text=%s depth=%d entry=%d expanded=%d children=[%s]>' % (repr(self.text), self.depth, self.entry, self.expanded, children)

class TreeList(Frame):
	selregex = re.compile('\\bsel\\b')

	def __init__(self, parent: Misc, selectmode: SelectMode = SINGLE, groupsel: bool = True, closeicon: Image | None = None, openicon: Image | None = None, height: int = 1, width: int = 1):
		self.selectmode = selectmode
		self.lastsel: int | None = None
		self.groupsel = groupsel
		self.entry = 0
		self.root = TreeGroup('<ROOT>', -1, -1, True)
		self.entries: dict[int, TreeNode] = {}
		if closeicon is None:
			closeicon = Assets.get_image('treeclose')
		if openicon is None:
			openicon = Assets.get_image('treeopen')
		self.icons = [closeicon,openicon]

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=height, width=width, font=Font.fixed(), wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=False)
		self.text.config(bd=0)
		self.text.configure(tabs=self.tk.call("font", "measure", self.text["font"], "-displayof", self, '  ') + openicon.width())
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.bind = self.text.bind # type: ignore[method-assign, assignment]

		text_w = getattr(self.text, '_w')
		self.text_orig = text_w + '_orig'
		self.tk.call('rename', text_w, self.text_orig)
		self.tk.createcommand(text_w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_config('Hightlight', background='#CCCCCC')

	def execute(self, cmd: str, args: tuple[str, ...]) -> str:
		try:
			return self.tk.call((self.text_orig, cmd) + args)
		except:
			return ""

	def dispatch(self, cmd: str, *args: str) -> str:
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)
		return ''

	def lookup_coords(self, x: int, y: int) -> tuple[str | None, bool]:
		index = self.index('@%d,%d' % (x,y))
		if index:
			for o in range(1,100):
				for below in (True,False):
					check = self.index('@%d,%d' % (x,y + o * (1 if below else -1)))
					if check != index:
						return (index, below)
		return (index,True)

	def index(self, entry: int | str) -> (str | None):
		index = None
		if isinstance(entry, str) and entry.startswith('@'):
			entries = [int(n[5:]) for n in self.text.tag_names(entry) if n.startswith('entry')]
			if entries:
				entry = entries[0]
		if isinstance(entry, int):
			node = self.entries[entry]
			index = ''
			while node and node != self.root:
				assert node.parent is not None
				index = '%d%s%s' % (node.parent.children.index(node),'.' if index else '',index)
				node = node.parent
		return index

	def get_node(self, index: int | str) -> (TreeNode | None):
		# print(('Get',index))
		node = None
		if isinstance(index, int):
			node = self.entries[index]
		elif isinstance(index, str):
			node = self.root
			if index:
				indices = [int(i) for i in index.split('.')]
				while indices:
					if not isinstance(node, TreeGroup):
						return None
					node = node.children[indices[0]]
					del indices[0]
		return node

	def node_visibility(self, node: TreeNode) -> bool:
		while node.parent and node.parent != self.root:
			if not node.parent.expanded:
				return False
			node = node.parent
		return True

	def cur_highlight(self) -> (int | None):
		ranges = self.text.tag_ranges('Hightlight')
		if ranges:
			entries = [int(n[5:]) for n in self.text.tag_names(ranges[0]) if n.startswith('entry')]
			if entries:
				return entries[0]
		return None

	def highlight(self, index: int | str | None) -> None:
		self.text.tag_remove('Hightlight', '1.0', END)
		if index is None:
			return
		node = self.get_node(index)
		if not node:
			return
		self.text.tag_add('Hightlight',  'entry%s.first' % node.entry, 'entry%s.last' % node.entry)

	def cur_selection(self) -> list[int]:
		s: list[int] = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([int(n[5:]) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

	def select(self, index: int | str | None, modifier: SelectModifier = SelectModifier.none) -> None:
		if index is None:
			self.text.tag_remove('Selection', '1.0', END)
			self.lastsel = None
			self.text.event_generate(WidgetEvent.Listbox.Select())
			return
		node = self.get_node(index)
		if node is None:
			return

		if modifier == SelectModifier.shift and self.selectmode == EXTENDED:
			if tuple(int(n) for n in self.text.index('entry%s.first' % self.lastsel).split('.')) > tuple(int(n) for n in self.text.index('entry%s.first' % node.entry).split('.')):
				d = '-1l'
			else:
				d = '+1l'
			c,f = self.text.index('entry%s.last %s lineend -1c' % (self.lastsel,d)),self.text.index('entry%s.last %s lineend -1c' % (node.entry,d))
			while c != f:
				r = self.text.tag_names(c)
				for e in r:
					if e.startswith('entry') and (self.groupsel or not isinstance(self.entries[int(e[5:])],TreeGroup)) and not 'Selection' in r:
						self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
				c = self.text.index('%s %s lineend -1c' % (c,d))
			self.lastsel = node.entry
		else:
			if self.selectmode != MULTIPLE or modifier != SelectModifier.ctrl:
				self.text.tag_remove('Selection', '1.0', END)
			if self.selectmode == EXTENDED:
				self.lastsel = node.entry
			if not self.selected(node.entry):
				self.text.tag_add('Selection',  'entry%s.first' % node.entry, 'entry%s.last' % node.entry)
		self.text.event_generate(WidgetEvent.Listbox.Select())

	def write_node(self, pos: str, node: TreeNode) -> None:
		# print(('Pos',pos))
		selectable = True
		if isinstance(node, TreeGroup):
			selectable = self.groupsel
			self.execute('insert',(pos, node.text, 'entry%s' % node.entry))
			self.execute('insert',(pos, '\t' * node.depth + '  '))
			self.execute('insert',('entry%s.last' % node.entry, '\n'))
			self.text.image_create('entry%s.first -1c' % node.entry, image=self.icons[node.expanded])
			self.text.tag_add('icon%s' % node.entry, 'entry%s.first -2c' % node.entry, 'entry%s.first -1c' % node.entry)
			def toggle_callback(entry: int) -> Callable[[Event], None]:
				def toggle(e: Event):
					self.toggle(entry)
				return toggle
			self.text.tag_bind('icon%s' % node.entry, Mouse.Click_Left(), toggle_callback(node.entry))
		else:
			self.execute('insert',(pos, node.text, 'entry%s' % node.entry))
			self.execute('insert',(pos, '\t' * (node.depth+1)))
			self.execute('insert',('entry%s.last' % node.entry, '\n'))
		if selectable:
			def select_callback(entry: int, modifier: SelectModifier) -> Callable[[Event], None]:
				def select(e: Event):
					self.select(entry, modifier)
				return select
			self.text.tag_bind('entry%s' % node.entry, Mouse.Click_Left(), select_callback(node.entry, SelectModifier.none))
			self.text.tag_bind('entry%s' % node.entry, Shift.Click_Left(), select_callback(node.entry, SelectModifier.shift))
			self.text.tag_bind('entry%s' % node.entry, Ctrl.Click_Left(), select_callback(node.entry, SelectModifier.ctrl))

	def erase_branch(self, node: TreeNode, eraseRoot: bool) -> None:
		end = 'entry%s.last lineend +1c' % node.entry
		if eraseRoot:
			start = 'entry%s.last linestart' % node.entry
		else:
			start = end
		while isinstance(node, TreeGroup) and node.expanded and node.children:
			deep_leaf = node.children[-1]
			end = 'entry%s.last lineend +1c' % deep_leaf.entry
			node = deep_leaf
		self.execute('delete', (start, end))

	def toggle(self, entry: int | str) -> None:
		group = self.get_node(entry)
		if not isinstance(group, TreeGroup):
			return
		expanded = not group.expanded
		self.text.image_configure('icon%s.first' % group.entry, image=self.icons[expanded])
		if expanded:
			base = 'icon%s.first' % group.entry
			def insert_children(group, line_offset=1):
				for child in group.children:
					self.write_node('%s +%sl linestart' % (base,line_offset), child)
					line_offset += 1
					if isinstance(child, TreeGroup) and child.expanded:
						line_offset += insert_children(child, line_offset)
				return line_offset
			insert_children(group)
		else:
			self.erase_branch(group, False)
		group.expanded = expanded

	def delete(self, index: int | str) -> None:
		if index == ALL:
			self.entry = 0
			self.root.children = []
			self.entries = {}
			self.execute('delete', ('1.0', END))
		else:
			eraseRoot = True
			# print(index)
			if isinstance(index, str):
				indices = index.split('.')
				if indices[-1] == ALL:
					eraseRoot = False
					index = '.'.join(indices[:-1])
			node = self.get_node(index)
			if not node:
				return
			if self.node_visibility(node):
				self.erase_branch(node, eraseRoot)
			def delete_node(node: TreeNode) -> None:
				del self.entries[node.entry]
				if isinstance(node, TreeGroup):
					for child in node.children:
						delete_node(child)
			if eraseRoot:
				if node.parent:
					node.parent.children.remove(node)
				delete_node(node)
			else:
				# for child in node.children:
				while isinstance(node, TreeGroup) and node.children:
					child = node.children[0]
					delete_node(child)
					del node.children[0]
			# print(self.entries)
			# print(self.root)

	# groupExpanded: None = not group, True = open by default, False = closed by default
	def insert(self, index: str, text: str, groupExpanded: bool | None = None) -> (str | None):
		# print(('Insert', index))
		indices = [int(i) for i in index.split('.')]
		parent_index = '.'.join(str(i) for i in indices[:-1])
		parent = self.get_node(parent_index)
		if not parent or not isinstance(parent, TreeGroup):
			return None
		insert_index = indices[-1]
		if insert_index == -1:
			insert_index = len(parent.children)
			indices[-1] = insert_index
		node: TreeNode
		if groupExpanded is not None:
			node = TreeGroup(text, parent.depth+1, self.entry, groupExpanded)
		else:
			node = TreeNode(text, parent.depth+1, self.entry)
		parent.add_child(node)
		self.entries[self.entry] = node
		self.entry += 1
		if self.node_visibility(node):
			base = '0.0'
			if len(parent.children) > 1:
				above = parent.children[-2]
				while isinstance(above, TreeGroup) and above.expanded and above.children:
					above = above.children[-1]
				base = 'entry%s.last +1l' % (above.entry)
			elif parent != self.root:
				base = 'entry%s.last +1l' % parent.entry
			self.write_node('%s linestart' % base, node)
		# print(self.entries)
		# print(self.root)
		return '.'.join(str(i) for i in indices)

	def get(self, index: int | str) -> (str | None):
		node = self.get_node(index)
		if not node:
			return None
		return node.text

	def get_visibility(self, index: int | str) -> bool:
		node = self.get_node(index)
		if not node:
			return False
		return self.node_visibility(node)

	def selected(self, index: int | str) -> bool:
		node = self.get_node(index)
		if not node:
			return False
		return ('Selection' in self.text.tag_names('entry%s.first' % node.entry))

	def set(self, index: int | str, text: str):
		node = self.get_node(index)
		if not node:
			return
		node.text = text
		selected = self.selected(index)
		start,end = tuple(str(i) for i in self.text.tag_ranges('entry%s' % node.entry))
		self.execute('delete', (start, end))
		self.execute('insert', (start, text, 'entry%s' % node.entry))
		if selected:
			self.text.tag_add('Selection', start, end)

	def see(self, index: int | str) -> None:
		node = self.get_node(index)
		if not node:
			return
		entry = 'entry%s' % node.entry
		ranges = self.text.tag_ranges(entry)
		if ranges:
			self.text.see(ranges[0])

	def build(self, tree: Sequence[tuple[Any, bool | None]], get_children: Callable[[Any], Sequence[tuple[Any, bool | None]]], get_name: Callable[[Any], str], index: str = '-1') -> None:
		for node,folder in tree:
			name = get_name(node)
			node_index = self.insert(index, name, folder)
			if not node_index:
				continue
			self.build(get_children(node), get_children, get_name, node_index + '.-1')

# import TBL,DAT
# class Test(Tk):
	# def __init__(self):
		# Tk.__init__(self)
		# self.title('TreeList Test')

		# self.tl = TreeList(self)
		# self.tl.pack(fill=BOTH, expand=1)
		# self.tl.insert('-1', 'Zerg', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('-1', 'Protoss', False)
		# self.tl.insert('-1', 'Other', False)

		# tbl = TBL.TBL()
		# tbl.load_file('Libs\\MPQ\\rez\\stat_txt.tbl')
		# dat = DAT.UnitsDAT()
		# dat.load_file('Libs\\MPQ\\arr\\units.dat')

		# groups = [{},{},{},{}]
		# for i,n in enumerate(TBL.decompile_string(s) for s in tbl.strings[:228]):
			# g = dat.get_value(i,'StarEditGroupFlags')
			# s = n.split('<0>')
			# found = False
			# if s[0] == 'Zerg Zergling':
				# g = 1|2|4
			# for f in [1,2,4,3]:
				# if (f != 3 and g & f) or (f == 3 and not found):
					# if not s[2] in groups[f-1]:
						# if f == 4:
							# e = '2'
						# elif f == 3:
							# e = '3'
						# else:
							# e = str(f-1)
						# groups[f-1][s[2]] = self.tl.insert(e + '.-1', s[2], False)
					# self.tl.insert(groups[f-1][s[2]] + '.-1', '[%s] %s%s' % (i,s[0],['',' (%s)' % s[1]][s[1] != '*']))
					# found = True
		# self.tl.insert('-1', 'Zerg', True)
		# self.tl.insert('0.-1', 'Ground Units', True)
		# self.tl.insert('0.0.-1', 'Zerg Zergling')
		# self.tl.insert('0.0.-1', 'Zerg Zergling', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('0', 'Test', False)
		# self.tl.bind('<Button-1>', self.test)
		# self.tl.bind('<Alt-d>', self.delete)
		# print(self.tl.groups)

	# def test(self, e):
		# print(self.tl.text.tag_ranges('Selection'))
		# s = self.tl.cur_selection()
		# print(s)
		# if s:
			# print(self.tl.get(s[0],True))

	# def delete(self, e):
		# self.tl.delete(self.tl.cur_selection())

# def main():
	# gui = Test()
	# gui.mainloop()

# if __name__ == '__main__':
	# main()
