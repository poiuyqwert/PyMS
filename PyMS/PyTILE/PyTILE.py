
from .TilePaletteView import TilePaletteView
from .MegaEditorView import MegaEditorView
from .TilePalette import TilePalette
from .Placeability import Placeability

from ..FileFormats.Tileset.Tileset import Tileset, TILETYPE_GROUP, TILETYPE_MEGA, megatile_to_photo, minitile_to_photo, HEIGHT_MID, HEIGHT_HIGH
from ..FileFormats import TBL

from ..Utilities.utils import WIN_REG_AVAILABLE, FFile, register_registry
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.SettingsDialog import SettingsDialog

LONG_VERSION = 'v%s' % Assets.version('PyTILE')

class PyTILE(MainWindow):
	def __init__(self, guifile=None):
		MainWindow.__init__(self)

		self.settings = Settings('PyTILE', '1')
		self.title('PyTILE %s' % LONG_VERSION)
		self.set_icon('PyTILE')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTILE', Assets.version('PyTILE'))
		ga.track(GAScreen('PyTILE'))
		setup_trace('PyTILE', self)
		Theme.load_theme(self.settings.get('theme'), self)

		self.stat_txt = TBL.TBL()
		self.stat_txt_file = ''
		filen = self.settings.files.get('stat_txt', Assets.mpq_file_path('rez', 'stat_txt.tbl'))
		while True:
			try:
				self.stat_txt.load_file(filen)
				break
			except:
				filen = self.settings.lastpath.tbl.select_open_file(self, title='Open stat_txt.tbl', filetypes=[FileType.tbl()])
				if not filen:
					sys.exit()

		self.loading_megas = False
		self.loading_minis = False
		self.tileset = None
		self.file = None
		self.edited = False
		self.megatile = None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('find'), lambda *_: self.choose(TILETYPE_GROUP), 'MegaTile Group Palette', Ctrl.p, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.cv5 editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTILE')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.disable = []

		self.megatilee = IntegerVar(0,[0,4095],callback=lambda id: self.change(TILETYPE_MEGA, int(id)))
		self.index = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.flags = IntegerVar(0,[0,15],callback=self.group_values_changed)
		self.groundheight = IntegerVar(0,[0,15],callback=self.group_values_changed)
		self.buildable = IntegerVar(0,[0,15],callback=self.group_values_changed)
		self.buildable2 = IntegerVar(0,[0,15],callback=self.group_values_changed)
		self.edgeleft = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.edgeright = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.edgeup = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.edgedown = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.hasup = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.hasdown = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.unknown9 = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.unknown11 = IntegerVar(0,[0,65535],callback=self.group_values_changed)
		self.doodad = False

		self.apply_all_exclude_nulls = IntVar()
		self.apply_all_exclude_nulls.set(self.settings.mega_edit.get('apply_all_exclude_nulls', True))

		self.copy_mega_height = IntVar()
		self.copy_mega_height.set(self.settings['copy'].mega.get('height', True))
		self.copy_mega_height.trace('w', self.action_states)
		self.copy_mega_walkable = IntVar()
		self.copy_mega_walkable.set(self.settings['copy'].mega.get('walkable', True))
		self.copy_mega_walkable.trace('w', self.action_states)
		self.copy_mega_sight = IntVar()
		self.copy_mega_sight.set(self.settings['copy'].mega.get('sight', True))
		self.copy_mega_sight.trace('w', self.action_states)
		self.copy_mega_ramp = IntVar()
		self.copy_mega_ramp.set(self.settings['copy'].mega.get('ramp', True))
		self.copy_mega_ramp.trace('w', self.action_states)

		self.copy_tilegroup_flags = IntVar()
		self.copy_tilegroup_flags.set(self.settings['copy'].tilegroup.get('flags', True))
		self.copy_tilegroup_flags.trace('w', self.action_states)
		self.copy_tilegroup_buildable = IntVar()
		self.copy_tilegroup_buildable.set(self.settings['copy'].tilegroup.get('buildable', True))
		self.copy_tilegroup_buildable.trace('w', self.action_states)
		self.copy_tilegroup_hasup = IntVar()
		self.copy_tilegroup_hasup.set(self.settings['copy'].tilegroup.get('hasup', True))
		self.copy_tilegroup_hasup.trace('w', self.action_states)
		self.copy_tilegroup_edges = IntVar()
		self.copy_tilegroup_edges.set(self.settings['copy'].tilegroup.get('edges', True))
		self.copy_tilegroup_edges.trace('w', self.action_states)
		self.copy_tilegroup_unknown9 = IntVar()
		self.copy_tilegroup_unknown9.set(self.settings['copy'].tilegroup.get('unknown9', True))
		self.copy_tilegroup_unknown9.trace('w', self.action_states)
		self.copy_tilegroup_index = IntVar()
		self.copy_tilegroup_index.set(self.settings['copy'].tilegroup.get('index', True))
		self.copy_tilegroup_index.trace('w', self.action_states)
		self.copy_tilegroup_buildable2 = IntVar()
		self.copy_tilegroup_buildable2.set(self.settings['copy'].tilegroup.get('buildable2', True))
		self.copy_tilegroup_buildable2.trace('w', self.action_states)
		self.copy_tilegroup_hasdown = IntVar()
		self.copy_tilegroup_hasdown.set(self.settings['copy'].tilegroup.get('hasdown', True))
		self.copy_tilegroup_hasdown.trace('w', self.action_states)
		self.copy_tilegroup_ground_height = IntVar()
		self.copy_tilegroup_ground_height.set(self.settings['copy'].tilegroup.get('ground_height', True))
		self.copy_tilegroup_ground_height.trace('w', self.action_states)
		self.copy_tilegroup_unknown11 = IntVar()
		self.copy_tilegroup_unknown11.set(self.settings['copy'].tilegroup.get('unknown11', True))
		self.copy_tilegroup_unknown11.trace('w', self.action_states)

		self.copy_doodadgroup_doodad = IntVar()
		self.copy_doodadgroup_doodad.set(self.settings['copy'].doodadgroup.get('doodad', True))
		self.copy_doodadgroup_doodad.trace('w', self.action_states)
		self.copy_doodadgroup_overlay = IntVar()
		self.copy_doodadgroup_overlay.set(self.settings['copy'].doodadgroup.get('overlay', True))
		self.copy_doodadgroup_overlay.trace('w', self.action_states)
		self.copy_doodadgroup_buildable = IntVar()
		self.copy_doodadgroup_buildable.set(self.settings['copy'].doodadgroup.get('buildable', True))
		self.copy_doodadgroup_buildable.trace('w', self.action_states)
		self.copy_doodadgroup_unknown1 = IntVar()
		self.copy_doodadgroup_unknown1.set(self.settings['copy'].doodadgroup.get('unknown1', True))
		self.copy_doodadgroup_unknown1.trace('w', self.action_states)
		self.copy_doodadgroup_unknown6 = IntVar()
		self.copy_doodadgroup_unknown6.set(self.settings['copy'].doodadgroup.get('unknown6', True))
		self.copy_doodadgroup_unknown6.trace('w', self.action_states)
		self.copy_doodadgroup_unknown8 = IntVar()
		self.copy_doodadgroup_unknown8.set(self.settings['copy'].doodadgroup.get('unknown8', True))
		self.copy_doodadgroup_unknown8.trace('w', self.action_states)
		self.copy_doodadgroup_unknown12 = IntVar()
		self.copy_doodadgroup_unknown12.set(self.settings['copy'].doodadgroup.get('unknown12', True))
		self.copy_doodadgroup_unknown12.trace('w', self.action_states)
		self.copy_doodadgroup_index = IntVar()
		self.copy_doodadgroup_index.set(self.settings['copy'].doodadgroup.get('index', True))
		self.copy_doodadgroup_index.trace('w', self.action_states)
		self.copy_doodadgroup_ground_height = IntVar()
		self.copy_doodadgroup_ground_height.set(self.settings['copy'].doodadgroup.get('ground_height', True))
		self.copy_doodadgroup_ground_height.trace('w', self.action_states)
		self.copy_doodadgroup_group_string_id = IntVar()
		self.copy_doodadgroup_group_string_id.set(self.settings['copy'].doodadgroup.get('group_string_id', True))
		self.copy_doodadgroup_group_string_id.trace('w', self.action_states)

		mid = Frame(self)
		self.palette = TilePaletteView(mid, TILETYPE_GROUP, delegate=self, multiselect=False, sub_select=True)
		self.palette.pack(side=LEFT, fill=Y)

		settings = Frame(mid)
		self.groupid = LabelFrame(settings, text='MegaTile Group')
		self.flow_view = FlowView(self.groupid, width=300)
		self.flow_view.pack(fill=BOTH, expand=1, padx=2)

		OPTION_RADIO = 0
		OPTION_CHECK = 1
		def options_editor(name, tooltip, variable, options):
			group = LabelFrame(self.flow_view.content_view, text=name)
			c = Frame(group)
			raw_tooltip = ''
			for option_name,option_value,option_tooltip,option_type,option_mask in options:
				raw_tooltip += '\n  %d = %s' % (option_value, option_name)
				if option_type == OPTION_CHECK and not option_value:
					continue
				f = Frame(c)
				if option_type == OPTION_CHECK:
					self.disable.append(MaskedCheckbutton(f, text=option_name, variable=variable, value=option_value, state=DISABLED))
				else:
					self.disable.append(MaskedRadiobutton(f, text=option_name, variable=variable, value=option_value, mask=option_mask if option_mask else variable.range[1], state=DISABLED))
				self.disable[-1].pack(side=LEFT)
				Tooltip(self.disable[-1], name + ':\n' + tooltip + '\n\n%s:\n  %s' % (option_name, option_tooltip))
				f.pack(side=TOP, fill=X)
			f = Frame(c)
			Label(f, text='Raw:').pack(side=LEFT)
			self.disable.append(Entry(f, textvariable=variable, font=Font.fixed(), width=len(str(variable.range[1])), state=DISABLED))
			self.disable[-1].pack(side=LEFT)
			Tooltip(self.disable[-1], name + ':\n' + tooltip + '\n\nRaw:' + raw_tooltip)
			f.pack(side=TOP, fill=X)
			c.pack(padx=2,pady=2)
			return group
		def entries_editor(name, tooltip, rows):
			group = LabelFrame(self.flow_view.content_view, text=name)
			f = Frame(group)
			for r,row in enumerate(rows):
				for c,(field_name, variable, field_tooltip) in enumerate(row):
					Label(f, text=field_name + ':').grid(column=c*2, row=r, sticky=E)
					self.disable.append(Entry(f, textvariable=variable, font=Font.fixed(), width=len(str(variable.range[1])), state=DISABLED))
					self.disable[-1].grid(column=c*2+1, row=r, sticky=W)
					if tooltip:
						Tooltip(self.disable[-1], name + ':\n' + tooltip + '\n\n%s:\n  %s' % (field_name, field_tooltip))
					else:
						Tooltip(self.disable[-1], field_name + ':\n' + field_tooltip)
			f.pack(padx=2,pady=2)
			return group
		def string_editor(name, tooltip, variable):
			group = LabelFrame(self.flow_view.content_view, text=name)
			f = Frame(group)
			Label(f, text='String:').grid(column=0,row=0, sticky=E)
			self.disable.append(DropDown(f, IntVar(), ['None'] + [TBL.decompile_string(s) for s in self.stat_txt.strings], variable, width=20))
			self.disable[-1].grid(sticky=W+E, column=1,row=0)
			Tooltip(self.disable[-1], name + ':\n' + tooltip)
			f.grid_columnconfigure(1, weight=1)
			Label(f, text='Raw:').grid(column=0,row=1, sticky=E)
			self.disable.append(Entry(f, textvariable=variable, font=Font.fixed(), width=len(str(variable.range[1])), state=DISABLED))
			self.disable[-1].grid(sticky=W, column=1,row=1)
			Tooltip(self.disable[-1], name + ':\n' + tooltip)
			f.pack(fill=BOTH, expand=1, padx=2,pady=2)
			return group
		def actions_editor(name, actions):
			group = LabelFrame(self.flow_view.content_view, text=name)
			f = Frame(group)
			for action_name,tooltip,callback in actions:
				self.disable.append(Button(f, text=action_name, command=callback))
				self.disable[-1].pack(fill=X, pady=(0,2))
				Tooltip(self.disable[-1], action_name + ':\n' + tooltip)
			f.pack(fill=BOTH, expand=1, padx=2,pady=(2,0))
			return group

		self.editor_configs = []

		self.normal_editors = []
		group = options_editor('Flags', 'Unknown', self.flags, (
			('Normal?', 0, 'Unknown', OPTION_RADIO, None),
			('Edge?', 1, 'Unknown', OPTION_RADIO, None),
			('Cliff?', 4, 'Unknown', OPTION_RADIO, None)
		))
		self.normal_editors.append(group)
		group = options_editor('Buildable', 'Default buildability property', self.buildable, (
			('Buildable', 0, 'All buildings buildable', OPTION_RADIO, None),
			('Creep', 4, 'Only Zerg buildings buildable', OPTION_RADIO, None),
			('Unbuildable', 8, 'No buildings buildable', OPTION_RADIO, None)
		))
		self.normal_editors.append(group)
		group = options_editor('Buildable 2', 'Buildability for Beacons/Start Location', self.buildable2, (
			('Default', 0, 'Use default buildability', OPTION_RADIO, None),
			('Buildable', 8, 'Beacons and Start Location are Buildable', OPTION_RADIO, None)
		))
		self.normal_editors.append(group)
		group = options_editor('Has Up', 'Edge piece has rows above it. Not completely understood.', self.hasup, (
			('None', 0, 'Unknown', OPTION_RADIO, None),
			('Basic edge piece', 1, 'Unknown', OPTION_RADIO, None),
			('Right edge piece', 2, 'Unknown', OPTION_RADIO, None),
			('Left edge piece', 3, 'Unknown', OPTION_RADIO, None)
		))
		self.normal_editors.append(group)
		group = options_editor('Has Down', 'Edge piece has rows below it. Not completely understood.', self.hasdown, (
			('None', 0, 'Unknown', OPTION_RADIO, None),
			('Basic edge piece', 1, 'Unknown', OPTION_RADIO, None),
			('Right edge piece', 2, 'Unknown', OPTION_RADIO, None),
			('Left edge piece', 3, 'Unknown', OPTION_RADIO, None)
		))
		self.normal_editors.append(group)
		group = entries_editor('Edges?', 'Unknown. Seems to be related to surrounding tiles & ISOM.', (
			(('Left?', self.edgeleft, 'Unknown.'), ('Up?', self.edgeup, 'Unknown.')),
			(('Right?', self.edgeright, 'Unknown.'), ('Down?', self.edgedown, 'Unknown.')),
		))
		self.normal_editors.append(group)
		group = entries_editor('Misc.', None, (
			(('Index', self.index, 'Group Index? Not completely understood'),),
			(('Ground Height', self.groundheight, 'Shows ground height. Does not seem to be completely valid.\n  May be used by StarEdit/deprecated?'),),
		))
		self.normal_editors.append(group)
		group = entries_editor('Unknowns', None, (
			(('Unknown 9', self.unknown9, 'Unknown'),),
			(('Unknown 11', self.unknown11, 'Unknown'),)
		))
		self.normal_editors.append(group)
		megatile_group = LabelFrame(self.flow_view.content_view, text='MegaTile')
		f = Frame(megatile_group)
		Label(f, text='ID:').pack(side=LEFT)
		self.disable.append(Entry(f, textvariable=self.megatilee, font=Font.fixed(), width=len(str(self.megatilee.range[1])), state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=2)
		Tooltip(self.disable[-1], 'MegaTile ID:\nID for the selected MegaTile in the current MegaTile Group')
		self.disable.append(Button(f, image=Assets.get_image('find'), width=20, height=20, command=lambda i=1: self.choose(i), state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=2)
		Tooltip(self.disable[-1], 'MegaTile Palette')
		f.pack(side=TOP, fill=X, padx=3)
		def megatile_apply_all_pressed():
			menu = Menu(self, tearoff=0)
			mode = self.mega_editor.edit_mode.get()
			name = [None,None,'Height','Walkability','Blocks View','Ramp(?)'][mode]
			menu.add_command(label="Apply %s flags to Megatiles in Group (Control+Shift+%s)" % (name, name[0]), command=lambda m=mode: self.megatile_apply_all(mode))
			menu.add_command(label="Apply all flags to Megatiles in Group (Control+Shift+A)", command=self.megatile_apply_all)
			menu.add_separator()
			menu.add_checkbutton(label="Exclude Null Tiles (Control+Shift+N)", variable=self.apply_all_exclude_nulls)
			menu.post(*self.winfo_pointerxy())
		self.apply_all_btn = Button(megatile_group, text='Apply to Megas', state=DISABLED, command=megatile_apply_all_pressed)
		self.disable.append(self.apply_all_btn)
		self.apply_all_btn.pack(side=BOTTOM, padx=3, pady=(0,3), fill=X)
		self.bind(Shift.Ctrl.h, lambda *_: self.megatile_apply_all(MegaEditorView.Mode.height))
		self.bind(Shift.Ctrl.w, lambda *_: self.megatile_apply_all(MegaEditorView.Mode.walkability))
		self.bind(Shift.Ctrl.b, lambda *_: self.megatile_apply_all(MegaEditorView.Mode.view_blocking))
		self.bind(Shift.Ctrl.r, lambda *_: self.megatile_apply_all(MegaEditorView.Mode.ramp))
		self.bind(Shift.Ctrl.a, lambda *_: self.megatile_apply_all(None))
		self.bind(Shift.Ctrl.n, lambda *_: self.apply_all_exclude_nulls.set(not self.apply_all_exclude_nulls.get()))
		self.mega_editor = MegaEditorView(megatile_group, self.settings, self, palette_editable=True)
		self.mega_editor.set_enabled(False)
		self.mega_editor.pack(side=TOP, padx=3, pady=(3,0))
		self.normal_editors.append(megatile_group)
		copy_mega_group = LabelFrame(self.flow_view.content_view, text='Copy MegaTile Flags')
		opts = (
			('Height', self.copy_mega_height),
			('Walkable', self.copy_mega_walkable),
			('Blocks Sight', self.copy_mega_sight),
			('Ramp', self.copy_mega_ramp)
		)
		for name,var in opts:
			check = Checkbutton(copy_mega_group, text=name, variable=var, anchor=W, state=DISABLED)
			check.grid(sticky=W)
			self.disable.append(check)
		def copy_mega(*args):
			if not self.tileset:
				return
			options = {
				'megatiles_export_height': self.copy_mega_height.get(),
				'megatiles_export_walkability': self.copy_mega_walkable.get(),
				'megatiles_export_block_sight': self.copy_mega_sight.get(),
				'megatiles_export_ramp': self.copy_mega_ramp.get(),
			}
			if not max(options.values()):
				return
			group = self.tileset.cv5.groups[self.palette.selected[0]]
			mega = group[13][self.palette.sub_selection]
			f = FFile()
			self.tileset.export_settings(TILETYPE_MEGA, f, [mega], options)
			self.clipboard_clear()
			self.clipboard_append(f.data)
		self.copy_mega_btn = Button(copy_mega_group, text='Copy (%s)' % Shift.Ctrl.c.description(), state=DISABLED, command=copy_mega)
		self.bind(Shift.Ctrl.c, copy_mega)
		self.copy_mega_btn.grid(sticky=E+W)
		def paste_mega(*args):
			if not self.tileset:
				return
			group = self.tileset.cv5.groups[self.palette.selected[0]]
			mega = group[13][self.palette.sub_selection]
			settings = self.clipboard_get()
			try:
				self.tileset.import_settings(TILETYPE_MEGA, settings, [mega])
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.mega_editor.draw()
			self.mark_edited()
		btn = Button(copy_mega_group, text='Paste (%s)' % Shift.Ctrl.v.description(), state=DISABLED, command=paste_mega)
		self.bind(Shift.Ctrl.v, paste_mega)
		btn.grid(sticky=E+W)
		self.disable.append(btn)
		self.normal_editors.append(copy_mega_group)
		copy_tilegroup_group = LabelFrame(self.flow_view.content_view, text='Copy Group Settings')
		opts = (
			(
				('Flags', self.copy_tilegroup_flags),
				('Buildable', self.copy_tilegroup_buildable),
				('Has Up', self.copy_tilegroup_hasup),
				('Edges', self.copy_tilegroup_edges),
				('Unknown 9', self.copy_tilegroup_unknown9),
			),
			(
				('Index', self.copy_tilegroup_index),
				('Buildable 2', self.copy_tilegroup_buildable2),
				('Has Down', self.copy_tilegroup_hasdown),
				('Ground Height', self.copy_tilegroup_ground_height),
				('Unknown 11', self.copy_tilegroup_unknown11)
			)
		)
		for c,rows in enumerate(opts):
			for r,(name,var) in enumerate(rows):
				check = Checkbutton(copy_tilegroup_group, text=name, variable=var, anchor=W, state=DISABLED)
				check.grid(column=c,row=r, sticky=W)
				self.disable.append(check)
		def copy_tilegroup(*args):
			if not self.tileset:
				return
			group = self.palette.selected[0]
			options = {}
			if group < 1024:
				options = {
					'groups_export_index': self.copy_tilegroup_index.get(),
					'groups_export_buildable': self.copy_tilegroup_buildable.get(),
					'groups_export_flags': self.copy_tilegroup_flags.get(),
					'groups_export_buildable2': self.copy_tilegroup_buildable2.get(),
					'groups_export_ground_height': self.copy_tilegroup_ground_height.get(),
					'groups_export_edge_left': self.copy_tilegroup_edges.get(),
					'groups_export_edge_up': self.copy_tilegroup_edges.get(),
					'groups_export_edge_right': self.copy_tilegroup_edges.get(),
					'groups_export_edge_down': self.copy_tilegroup_edges.get(),
					'groups_export_unknown9': self.copy_tilegroup_unknown9.get(),
					'groups_export_has_up': self.copy_tilegroup_hasup.get(),
					'groups_export_unknown11': self.copy_tilegroup_unknown11.get(),
					'groups_export_has_down': self.copy_tilegroup_hasdown.get(),
				}
			else:
				options = {
					'groups_export_index': self.copy_doodadgroup_index.get(),
					'groups_export_buildable': self.copy_doodadgroup_buildable.get(),
					'groups_export_unknown1': self.copy_doodadgroup_unknown1.get(),
					'groups_export_overlay_flags': self.copy_doodadgroup_overlay.get(),
					'groups_export_ground_height': self.copy_doodadgroup_ground_height.get(),
					'groups_export_overlay_id': self.copy_doodadgroup_overlay.get(),
					'groups_export_unknown6': self.copy_doodadgroup_unknown6.get(),
					'groups_export_doodad_group_string': self.copy_doodadgroup_group_string_id.get(),
					'groups_export_unknown8': self.copy_doodadgroup_unknown8.get(),
					'groups_export_dddata_id': self.copy_doodadgroup_doodad.get(),
					'groups_export_doodad_width': self.copy_doodadgroup_doodad.get(),
					'groups_export_doodad_height': self.copy_doodadgroup_doodad.get(),
					'groups_export_unknown12': self.copy_doodadgroup_unknown12.get(),
				}
			if not max(options.values()):
				return
			f = FFile()
			self.tileset.export_settings(TILETYPE_GROUP, f, [group], options)
			self.clipboard_clear()
			self.clipboard_append(f.data)
		self.copy_tilegroup_btn = Button(copy_tilegroup_group, text='Copy (%s)' % Ctrl.Alt.c.description(), state=DISABLED, command=copy_tilegroup)
		self.bind(Ctrl.Alt.c, copy_tilegroup)
		self.copy_tilegroup_btn.grid(column=0,row=5, sticky=E+W)
		def paste_tilegroup(*args):
			if not self.tileset:
				return
			group = self.palette.selected[0]
			settings = self.clipboard_get()
			try:
				self.tileset.import_settings(TILETYPE_GROUP, settings, [group])
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.megaload()
			self.mark_edited()
		btn = Button(copy_tilegroup_group, text='Paste (%s)' % Ctrl.Alt.v.description(), state=DISABLED, command=paste_tilegroup)
		self.bind(Ctrl.Alt.v, paste_tilegroup)
		btn.grid(column=1,row=5, sticky=E+W)
		self.disable.append(btn)
		self.normal_editors.append(copy_tilegroup_group)


		self.doodad_editors = []

		group = entries_editor('Doodad', 'Basic doodad properties', (
			(('ID', self.edgeright, 'Each doodad must have a unique Doodad ID.\n  All MegaTile Groups in the doodad must have the same ID.'),),
			(('Width', self.edgeup, 'Total width of the doodad in MegaTiles'),),
			(('Height', self.edgedown, 'Total height of the doodad in MegaTiles'),),
		))
		self.doodad_editors.append(group)
		group = options_editor('Has Overlay', 'Doodad overlay settings', self.buildable2, (
			('None', 0, 'No overlay', OPTION_RADIO, 3),
			('Sprites.dat', 1, 'The overlay ID is a Sprites.dat reference.', OPTION_RADIO, 3),
			('Units.dat', 2, 'The overlay ID is a Units.dat reference', OPTION_RADIO, 3),
			('Flipped', 4, 'The overlay is flipped.', OPTION_CHECK, None),
		))
		self.doodad_editors.append(group)
		group = entries_editor('Overlay', None, (
			(('ID', self.hasup, 'Sprite or Unit ID (depending on the Has Overlay flag) of the doodad overlay.'),),
		))
		self.doodad_editors.append(group)
		group = options_editor('Buildable', 'Default buildability property', self.buildable, (
			('Buildable', 0, 'All buildings buildable', OPTION_CHECK, None),
			('Unknown', 1, 'Unknown', OPTION_CHECK, None),
			('Creep', 4, 'Only Zerg buildings buildable', OPTION_RADIO, 12),
			('Unbuildable', 8, 'No buildings buildable', OPTION_RADIO, 12),
		))
		self.doodad_editors.append(group)
		group = entries_editor('Unknowns', None, (
			(('Unknown 1', self.flags, 'Unknown'),),
			(('Unknown 6', self.hasdown, 'Unknown'),),
			(('Unknown 8', self.unknown9, 'Unknown'),),
			(('Unknown 12', self.unknown11, 'Unknown'),)
		))
		self.doodad_editors.append(group)
		group = entries_editor('Misc.', None, (
			(('Index', self.index, 'Group Index? Not completely understood'),),
			(('Ground Height', self.groundheight, 'Shows ground height. Does not seem to be completely valid.\n  May be used by StarEdit/deprecated?'),),
		))
		self.doodad_editors.append(group)
		group = string_editor('Group', 'Doodad group string from stat_txt.tbl', self.edgeleft)
		self.doodad_editors.append(group)
		self.editor_configs.append((group, {'weight': 1}))
		group = actions_editor('Other', (
			('Placeability', 'Modify which megatile groups the doodad must be placed on.', self.placeability),
			('Apply All', 'Apply these MegaTile Group settings to all the MegaTile Groups with the same Doodad ID', self.doodad_apply_all)
		))
		self.doodad_editors.append(group)
		self.doodad_editors.append(megatile_group)
		self.doodad_editors.append(copy_mega_group)
		copy_doodadgroup_group = LabelFrame(self.flow_view.content_view, text='Copy Group Settings')
		opts = (
			(
				('Doodad', self.copy_doodadgroup_doodad),
				('Buildable', self.copy_doodadgroup_buildable),
				('Index', self.copy_doodadgroup_index),
				('Unknown 1', self.copy_doodadgroup_unknown1),
				('Unknown 6', self.copy_doodadgroup_unknown6),
			),
			(
				('Overlay', self.copy_doodadgroup_overlay),
				('Ground Height', self.copy_doodadgroup_ground_height),
				('Group String', self.copy_doodadgroup_group_string_id),
				('Unknown 8', self.copy_doodadgroup_unknown8),
				('Unknown 12', self.copy_doodadgroup_unknown12),
			)
		)
		for c,rows in enumerate(opts):
			for r,(name,var) in enumerate(rows):
				check = Checkbutton(copy_doodadgroup_group, text=name, variable=var, anchor=W, state=DISABLED)
				check.grid(column=c,row=r, sticky=W)
				self.disable.append(check)
		self.copy_doodadgroup_btn = Button(copy_doodadgroup_group, text='Copy (%s)' % Ctrl.Alt.c.description(), state=DISABLED, command=copy_tilegroup)
		self.bind(Ctrl.Alt.c, copy_tilegroup)
		self.copy_doodadgroup_btn.grid(column=0,row=5, sticky=E+W)
		btn = Button(copy_doodadgroup_group, text='Paste (%s)' % Ctrl.Alt.v.description(), state=DISABLED, command=paste_tilegroup)
		self.bind(Ctrl.Alt.v, paste_tilegroup)
		btn.grid(column=1,row=5, sticky=E+W)
		self.disable.append(btn)
		self.doodad_editors.append(copy_doodadgroup_group)
		self.flow_view.add_subviews(self.normal_editors, padx=2)

		self.groupid.pack(fill=BOTH, expand=1, padx=5, pady=5)
		settings.pack(side=LEFT, fill=BOTH, expand=1)
		mid.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.expanded = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=45, anchor=W).pack(side=LEFT, padx=1)
		self.editstatus = Label(statusbar, image=Assets.get_image('save'), bd=0, state=DISABLED)
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.expanded, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load a Tileset.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyTILE')

	def tile_palette_get_tileset(self):
		return self.tileset

	def tile_palette_get_tile(self):
		return self.gettile

	def tile_palette_binding_widget(self):
		return self

	def tile_palette_bind_updown(self):
		return False

	def tile_palette_selection_changed(self):
		self.megaload()

	def is_file_open(self):
		return not not self.tileset

	def unsaved(self):
		if self.is_file_open() and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.cv5'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def action_states(self, *args, **kwargs):
		is_file_open = self.is_file_open()

		self.toolbar.tag_enabled('file_open', is_file_open)
		for w in self.disable:
			w['state'] = NORMAL if is_file_open else DISABLED
		self.mega_editor.set_enabled(is_file_open)

		if is_file_open and self.tileset.vx4.expanded:
			self.expanded.set('VX4 Expanded')
		
		can_copy_mega = is_file_open and (self.copy_mega_height.get() or self.copy_mega_walkable.get() or self.copy_mega_sight.get() or self.copy_mega_ramp.get())
		self.copy_mega_btn['state'] = NORMAL if can_copy_mega else DISABLED

		can_copy_group = is_file_open and (self.copy_tilegroup_flags.get() or self.copy_tilegroup_buildable.get() or self.copy_tilegroup_hasup.get() or self.copy_tilegroup_edges.get() or self.copy_tilegroup_unknown9.get() or self.copy_tilegroup_index.get() or self.copy_tilegroup_buildable2.get() or self.copy_tilegroup_hasdown.get() or self.copy_tilegroup_ground_height.get() or self.copy_tilegroup_unknown11.get())
		self.copy_tilegroup_btn['state'] = NORMAL if can_copy_group else DISABLED

		can_copy_doodadgroup = is_file_open and (self.copy_doodadgroup_doodad.get() or self.copy_doodadgroup_overlay.get() or self.copy_doodadgroup_buildable.get() or self.copy_doodadgroup_unknown1.get() or self.copy_doodadgroup_unknown6.get() or self.copy_doodadgroup_unknown8.get() or self.copy_doodadgroup_unknown12.get() or self.copy_doodadgroup_index.get() or self.copy_doodadgroup_ground_height.get() or self.copy_doodadgroup_group_string_id.get())
		self.copy_doodadgroup_btn['state'] = NORMAL if can_copy_doodadgroup else DISABLED

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def gettile(self, id, cache=False):
		to_photo = [megatile_to_photo,minitile_to_photo][isinstance(id,tuple) or isinstance(id,list)]
		if cache:
			if not id in TilePalette.TILE_CACHE:
				TilePalette.TILE_CACHE[id] = to_photo(self.tileset, id)
			return TilePalette.TILE_CACHE[id]
		return to_photo(self.tileset, id)

	def megatile_apply_all(self, mode=None):
		if not self.tileset:
			return
		copy_mask = ~0
		if mode == MegaEditorView.Mode.height:
			copy_mask = HEIGHT_MID | HEIGHT_HIGH
		elif mode == MegaEditorView.Mode.walkability:
			copy_mask = 1
		elif mode == MegaEditorView.Mode.view_blocking:
			copy_mask = 8
		elif mode == MegaEditorView.Mode.ramp:
			copy_mask = 16
		copy_mega = self.tileset.cv5.groups[self.palette.selected[0]][13][self.palette.sub_selection]
		edited = False
		for m in self.tileset.cv5.groups[self.palette.selected[0]][13]:
			if m == copy_mega or (m == 0 and self.apply_all_exclude_nulls.get()):
				continue
			for n in range(16):
				copy_flags = self.tileset.vf4.flags[copy_mega][n]
				flags = self.tileset.vf4.flags[m][n]
				new_flags = (flags & ~copy_mask) | (copy_flags & copy_mask)
				if new_flags != flags:
					self.tileset.vf4.flags[m][n] = new_flags
					edited = True
		if edited:
			self.mark_edited()

	def doodad_apply_all(self):
		doodad_id = self.edgeright.get()
		settings = self.tileset.cv5.groups[self.palette.selected[0]][:-1]
		for i in range(1024, len(self.tileset.cv5.groups)):
			if i != self.palette.selected[0] and self.tileset.cv5.groups[i][9] == doodad_id:
				self.tileset.cv5.groups[i][:-1] = settings

	def mega_edit_mode_updated(self, mode):
		if mode == MegaEditorView.Mode.mini or mode == MegaEditorView.Mode.flip:
			self.apply_all_btn.pack_forget()
		else:
			self.apply_all_btn.pack()

	def update_group_label(self):
		d = ['',' - Doodad'][self.palette.selected[0] >= 1024]
		self.groupid['text'] = 'MegaTile Group [%s%s]' % (self.palette.selected[0],d)

	def megaload(self):
		self.loading_megas = True
		group = self.tileset.cv5.groups[self.palette.selected[0]]
		mega = group[13][self.palette.sub_selection]
		if self.megatilee.get() != mega:
			self.megatilee.check = False
			self.megatilee.set(mega)
			self.megatilee.check = True
		if self.palette.selected[0] >= 1024:
			if not self.doodad:
				self.flow_view.remove_all_subviews()
				self.flow_view.add_subviews(self.doodad_editors, padx=2)
				for view,config in self.editor_configs:
					self.flow_view.update_subview_config(view, **config)
				self.doodad = True
			o = [self.index,self.buildable,self.flags,self.buildable2,self.groundheight,self.hasup,self.hasdown,self.edgeleft,self.unknown9,self.edgeright,self.edgeup,self.edgedown,self.unknown11]
		else:
			if self.doodad:
				self.flow_view.remove_all_subviews()
				self.flow_view.add_subviews(self.normal_editors, padx=2)
				for view,config in self.editor_configs:
					self.flow_view.update_subview_config(view, **config)
				self.doodad = False
			o = [self.index,self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]
		for n,v in enumerate(o):
			v.set(group[n])
		self.miniload()
		self.update_group_label()
		self.loading_megas = False

	def miniload(self):
		self.mega_editor.set_megatile(self.tileset.cv5.groups[self.palette.selected[0]][13][self.palette.sub_selection])

	def group_values_changed(self, *_):
		if not self.tileset or self.loading_megas:
			return
		group = self.tileset.cv5.groups[self.palette.selected[0]]
		group[0] = self.index.get()
		if self.palette.selected[0] >= 1024:
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.hasup,self.hasdown,self.edgeleft,self.unknown9,self.edgeright,self.edgeup,self.edgedown,self.unknown11]
		else:
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]
		for n,v in enumerate(o):
			group[n+1] = v.get()
		self.mark_edited()

	def choose(self, tile_type):
		TilePalette(
			self,
			self.settings,
			tile_type,
			self.palette.selected[0] if tile_type == TILETYPE_GROUP else self.tileset.cv5.groups[self.palette.selected[0]][13][self.palette.sub_selection],
			editing=True
		)

	def change(self, tiletype, id):
		if not self.tileset:
			return
		if tiletype == TILETYPE_GROUP:
			self.palette.select(id, sub_select=0, scroll_to=True)
		elif tiletype == TILETYPE_MEGA and not self.loading_megas:
			self.tileset.cv5.groups[self.palette.selected[0]][13][self.palette.sub_selection] = id
			self.palette.draw_tiles(force=True)
			self.mega_editor.set_megatile(id)
			self.mark_edited()

	def placeability(self):
		Placeability(self, self.settings, self.edgeright.get())

	def update_ranges(self):
		self.megatilee.setrange([0,len(self.tileset.vf4.flags)-1])
		self.mega_editor.update_mini_range()
		self.palette.update_size()
		self.palette.draw_tiles(force=True)

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file is None:
				file = self.settings.lastpath.tileset.select_open_file(self, title='Open Complete Tileset', filetypes=[FileType.cv5()])
				if not file:
					return
			tileset = Tileset()
			try:
				tileset.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.tileset = tileset
			self.file = file
			self.status.set('Load successful!')
			self.mark_edited(False)
			self.action_states()
			self.update_ranges()
			self.palette.update_size()
			self.palette.select(0)
			if self.tileset.vx4.expanded:
				self.settings.dont_warn.warn('expanded_vx4', self, "This tileset is using an expanded vx4 file (vx4ex). This could be a Remastered tileset, and/or will require a 'VX4 Expander Plugin' for pre-Remastered.")

	def save(self, key=None):
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.settings.lastpath.tileset.select_save_file(self, title='Save Tileset As', filetypes=[FileType.cv5()])
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.tileset.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
		self.file = file_path
		self.status.set('Save Successful!')
		self.mark_edited(False)

	def close(self, key=None):
		if not self.is_file_open():
			return
		if not self.unsaved():
			self.tileset = None
			self.file = None
			self.status.set('Load or create a Tileset.')
			self.mark_edited(False)
			self.groupid['text'] = 'MegaTile Group'
			if self.doodad:
				self.doodads.pack_forget()
				self.tiles.pack(side=TOP)
				self.doodad = False
			self.mega_editor.set_megatile(None)
			for v in [self.index,self.megatilee,self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]:
				v.set(0)
			self.palette.draw_tiles()
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyTILE', 'cv5', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def sets(self, key=None, err=None):
		SettingsDialog(self, [('Theme',)], (550,380), err, settings=self.settings)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyTILE.md')

	def about(self, key=None):
		AboutDialog(self, 'PyTILE', LONG_VERSION, [('FaRTy1billion','Tileset file specs and HawtTiles.')])

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.mega_edit.apply_all_exclude_nulls = not not self.apply_all_exclude_nulls.get()
			self.settings['copy'].mega.height = not not self.copy_mega_height.get()
			self.settings['copy'].mega.walkable = not not self.copy_mega_walkable.get()
			self.settings['copy'].mega.sight = not not self.copy_mega_sight.get()
			self.settings['copy'].mega.ramp = not not self.copy_mega_ramp.get()
			self.settings['copy'].tilegroup.flags = not not self.copy_tilegroup_flags.get()
			self.settings['copy'].tilegroup.buildable = not not self.copy_tilegroup_buildable.get()
			self.settings['copy'].tilegroup.hasup = not not self.copy_tilegroup_hasup.get()
			self.settings['copy'].tilegroup.edges = not not self.copy_tilegroup_edges.get()
			self.settings['copy'].tilegroup.unknown9 = not not self.copy_tilegroup_unknown9.get()
			self.settings['copy'].tilegroup.index = not not self.copy_tilegroup_index.get()
			self.settings['copy'].tilegroup.buildable2 = not not self.copy_tilegroup_buildable2.get()
			self.settings['copy'].tilegroup.hasdown = not not self.copy_tilegroup_hasdown.get()
			self.settings['copy'].tilegroup.ground_height = not not self.copy_tilegroup_ground_height.get()
			self.settings['copy'].tilegroup.unknown11 = not not self.copy_tilegroup_unknown11.get()
			self.settings['copy'].doodadgroup.doodad = not not self.copy_doodadgroup_doodad.get()
			self.settings['copy'].doodadgroup.overlay = not not self.copy_doodadgroup_overlay.get()
			self.settings['copy'].doodadgroup.buildable = not not self.copy_doodadgroup_buildable.get()
			self.settings['copy'].doodadgroup.unknown1 = not not self.copy_doodadgroup_unknown1.get()
			self.settings['copy'].doodadgroup.unknown6 = not not self.copy_doodadgroup_unknown6.get()
			self.settings['copy'].doodadgroup.unknown8 = not not self.copy_doodadgroup_unknown8.get()
			self.settings['copy'].doodadgroup.unknown12 = not not self.copy_doodadgroup_unknown12.get()
			self.settings['copy'].doodadgroup.index = not not self.copy_doodadgroup_index.get()
			self.settings['copy'].doodadgroup.ground_height = not not self.copy_doodadgroup_ground_height.get()
			self.settings['copy'].doodadgroup.group_string_id = not not self.copy_doodadgroup_group_string_id.get()
			self.settings.save()
			self.destroy()
