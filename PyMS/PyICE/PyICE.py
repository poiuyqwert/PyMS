
from .Config import PyICEConfig
from .Delegates import MainDelegate, ImportListDelegate
from .ImportListDialog import ImportListDialog
from .FindDialog import FindDialog
from .CodeEditDialog import CodeEditDialog
from .SettingsUI.SettingsDialog import SettingsDialog

from ..FileFormats.IScriptBIN import IScriptBIN
from ..FileFormats.IScriptBIN.IScript import IScript
from ..FileFormats.IScriptBIN.CodeHandlers import DataContext, ICEParseContext, ICESerializeContext, ICELexer
from ..FileFormats import TBL
from ..FileFormats import DAT

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.PyMSWarning import PyMSWarning
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities import IO
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate
from ..Utilities.SponsorDialog import SponsorDialog

from enum import IntEnum

from typing import IO as BuiltinIO

LONG_VERSION = 'v%s' % Assets.version('PyICE')

class ColumnID(IntEnum):
	IScripts = 0
	Images = 1
	Sprites = 2
	Flingys = 3
	Units = 4

class PyICE(MainWindow, MainDelegate, ImportListDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyICE')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyICE', Assets.version('PyICE'))
		ga.track(GAScreen('PyICE'))
		setup_trace('PyICE', self)

		self.config_ = PyICEConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.file: str | None = None
		self.data_context = DataContext()
		self.ibin: IScriptBIN.IScriptBIN | None = None
		self.edited = False

		self.update_title()

		self.findhistory: list[str] = []
		self.replacehistory: list[str] = []
		self.imports: list[str] = []

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n),
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default Scripts', Ctrl.d)
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Entries', Ctrl.Alt.e, enabled=False, tags='entries_selected')
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Entries', Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('listimport'), self.listimport, 'Import a List of Files', Ctrl.l, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Entries', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('codeedit'), self.codeedit, 'Edit IScript entries', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.tblbin, 'Manage TBL and DAT files', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE),
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyICE')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		#listbox,etc.
		listframes = Frame(self)
		def listbox_colum(name):
			f = Frame(listframes)
			Label(f, text=name + ':', anchor=W).pack(fill=X)
			listbox = ScrolledListbox(f, selectmode=MULTIPLE, font=Font.fixed(), width=1, height=1)
			listbox.bind(WidgetEvent.Listbox.Select, lambda _,l=listbox: self.listbox_selection_changed(l))
			listbox.pack(fill=BOTH, expand=1)
			Button(f, text='Unselect All', command=lambda l=listbox: self.unselect(l)).pack(fill=X)
			f.pack(side=LEFT, fill=BOTH, padx=2, expand=1)
			return listbox
		self.iscriptlist = listbox_colum('IScript Entries')
		self.imageslist = listbox_colum('Images')
		self.spriteslist = listbox_colum('Sprites')
		self.flingylist = listbox_colum("Flingy's")
		self.unitlist = listbox_colum('Units')
		listframes.pack(fill=BOTH, pady=2, expand=1)

		self.bind(Ctrl.a(), lambda *e: self.select_all())

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a BIN.')
		self.selectstatus = StringVar()
		self.selectstatus.set("IScript ID's Selected: None")
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.selectstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.config_.windows.main.load_size(self)

		self.mpqhandler = MPQHandler(self.config_.mpqs)

	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.tblbin(err=e)
		if self.guifile:
			self.open(file=self.guifile)
		UpdateDialog.check_update(self, 'PyICE')

	def select_all(self) -> None:
		self.iscriptlist.select_set(0, END)
		self.action_states()

	def open_files(self) -> PyMSError | None:
		self.mpqhandler.open_mpqs()
		err: PyMSError | None = None
		try:
			stat_txt = TBL.TBL()
			imagestbl = TBL.TBL()
			sfxdatatbl = TBL.TBL()
			unitsdat = DAT.UnitsDAT()
			weaponsdat = DAT.WeaponsDAT()
			flingydat = DAT.FlingyDAT()
			spritesdat = DAT.SpritesDAT()
			imagesdat = DAT.ImagesDAT()
			soundsdat = DAT.SoundsDAT()
			stat_txt.load_file(self.mpqhandler.load_file(self.config_.settings.files.tbl.stat_txt.file_path))
			imagestbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.tbl.images.file_path))
			sfxdatatbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.tbl.sfxdata.file_path))
			unitsdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.units.file_path))
			weaponsdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.weapons.file_path))
			flingydat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.flingy.file_path))
			spritesdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.sprites.file_path))
			imagesdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.images.file_path))
			soundsdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.sfxdata.file_path))
		except PyMSError as e:
			err = e
		else:
			self.data_context.set_stat_txt_tbl(stat_txt)
			self.data_context.set_images_tbl(imagestbl)
			self.data_context.set_sounds_tbl(sfxdatatbl)
			self.unitsdat = unitsdat # TODO: units.dat?
			self.data_context.set_weapons_dat(weaponsdat)
			self.data_context.set_flingy_dat(flingydat)
			self.data_context.set_sprites_dat(spritesdat)
			self.data_context.set_images_dat(imagesdat)
			self.data_context.set_sounds_dat(soundsdat)
			try:
				unitnamestbl = TBL.TBL()
				unitnamestbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.tbl.unitnames.file_path))
			except:
				self.unitnamestbl = None # TODO: Unitnames.tbl?
			else:
				self.unitnamestbl = unitnamestbl
			self.update_dat_lists()
		self.mpqhandler.close_mpqs()
		return err

	# def get_image_names(self) -> tuple[str, ...]:
	# 	return tuple(DAT.DATEntryName.image(entry_id, data_names=Assets.data_cache(Assets.DataReference.Images)) for entry_id in range(self.imagesdat.entry_count()))

	# def get_sprite_names(self) -> tuple[str, ...]:
	# 	return tuple(DAT.DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sprites)) for entry_id in range(self.spritesdat.entry_count()))

	# def get_flingy_names(self) -> tuple[str, ...]:
	# 	return tuple(DAT.DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Flingy)) for entry_id in range(self.flingydat.entry_count()))

	def get_unit_names(self) -> tuple[str, ...]:
		return tuple(DAT.DATEntryName.unit(entry_id, stat_txt=self.data_context.stat_txt_tbl, unitnamestbl=self.unitnamestbl, data_names_usage=DAT.DataNamesUsage.ignore) for entry_id in range(self.unitsdat.entry_count()))

	def update_dat_lists(self) -> None:
		updates = (
			(self.data_context.get_image_names(), ColumnID.Images, self.imageslist),
			(self.data_context.get_sprite_names(), ColumnID.Sprites, self.spriteslist),
			(self.data_context.get_flingy_names(), ColumnID.Flingys, self.flingylist),
			(self.get_unit_names(), ColumnID.Units, self.unitlist)
		)
		for names, column, listbox in updates:
			listbox.delete(0,END)
			for index,name in enumerate(names):
				listbox.insert(END, '%03s %s [%s]' % (index, name, self.iscript_id_from_selection_index(index, column)))
		self.action_states()

	def _sorted_scripts(self) -> list[IScript]:
		if not self.ibin:
			return []
		return sorted(self.ibin.list_scripts(), key=lambda script: script.id)

	def update_iscrips_list(self) -> None:
		self.iscriptlist.delete(0,END)
		if not self.ibin:
			return
		scripts = self._sorted_scripts()
		for iscript in scripts:
			iscript_id = iscript.id
			if iscript_id < len(Assets.data_cache(Assets.DataReference.IscriptIDList)):
				name = Assets.data_cache(Assets.DataReference.IscriptIDList)[iscript_id]
			else:
				name = 'Unnamed Custom Entry'
			self.iscriptlist.insert(END, '%03s %s' % (iscript_id, name))

	def iscript_id_from_selection_index(self, index: int, column: ColumnID) -> int:
		if column == ColumnID.IScripts:
			assert self.ibin is not None
			return self._sorted_scripts()[index].id
		if column >= ColumnID.Units:
			index = self.unitsdat.get_entry(index).graphics
		if column >= ColumnID.Flingys:
			assert self.data_context.flingy_dat is not None # TODO: Missing DAT files?
			index = self.data_context.flingy_dat.get_entry(index).sprite
		if column >= ColumnID.Sprites:
			assert self.data_context.sprites_dat is not None # TODO: Missing DAT files?
			index = self.data_context.sprites_dat.get_entry(index).image
		assert self.data_context.images_dat is not None # TODO: Missing DAT files?
		return self.data_context.images_dat.get_entry(index).iscript_id

	def selected_iscript_ids(self) -> list[int]:
		iscript_ids: list[int] = []
		lists = (
			(ColumnID.IScripts, self.iscriptlist),
			(ColumnID.Units, self.unitlist),
			(ColumnID.Flingys, self.flingylist),
			(ColumnID.Sprites, self.spriteslist),
			(ColumnID.Images, self.imageslist)
		)
		for column,listbox in lists:
			selected_indexes = listbox.curselection()
			for index in selected_indexes:
				iscript_id = self.iscript_id_from_selection_index(index, column)
				if not iscript_id in iscript_ids:
					iscript_ids.append(iscript_id)
		return sorted(iscript_ids)

	def unselect(self, listbox) -> None:
		listbox.select_clear(0, END)
		self.listbox_selection_changed()

	def listbox_selection_changed(self, listbox: Listbox | None = None) -> None:
		iscript_ids = self.selected_iscript_ids()
		if iscript_ids:
			self.selectstatus.set("IScript ID's Selected: %s" % ', '.join([str(i) for i in iscript_ids]))
		else:
			self.selectstatus.set("IScript ID's Selected: None")
		self.action_states()
		if listbox:
			listbox.focus_set()

	def is_file_open(self) -> bool:
		return not not self.ibin

	def action_states(self) -> None:
		is_file_open = self.is_file_open()
		for listbox in [self.imageslist,self.spriteslist,self.flingylist,self.unitlist]:
			listbox.listbox['state'] = NORMAL if is_file_open else DISABLED
		self.toolbar.tag_enabled('file_open', is_file_open)

		entries_selected = not not self.selected_iscript_ids()
		self.toolbar.tag_enabled('entries_selected', entries_selected)

	def check_saved(self) -> CheckSaved:
		if not self.ibin or not self.edited:
			return CheckSaved.saved
		iscript = self.file
		if not iscript:
			iscript = 'iscript.bin'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % iscript, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file:
			return self.save()
		else:
			return self.saveas()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.bin'
		if not file_path:
			self.title('PyICE %s' % LONG_VERSION)
		else:
			self.title('PyICE %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.iscriptlist.delete(0,END)
		self.ibin = IScriptBIN.IScriptBIN()
		self.file = None
		self.status.set('Editing new BIN.')
		self.update_title()
		self.action_states()
		self.mark_edited(False)

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.bin.select_open(self)
			if not file:
				return
		ibin = IScriptBIN.IScriptBIN()
		try:
			ibin.load(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.ibin = ibin
		self.update_iscrips_list()
		self.file = file
		self.update_title()
		self.status.set('Load Successful!')
		self.action_states()
		self.mark_edited(False)

	def open_default(self) -> None:
		self.open(Assets.mpq_file_path('scripts','iscript.bin'))

	def save(self) -> CheckSaved:
		return self.saveas(self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.ibin:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.bin.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.ibin.save(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)
		return CheckSaved.saved

	def iimport(self, files: str | list[str] | None = None, parent: Misc | None = None) -> None:
		if not self.ibin:
			return
		if not files:
			files = self.config_.last_path.txt.select_open_multiple(self)
		if not files:
			return
		if not isinstance(files, list):
			files = [files]
		if parent is None:
			parent = self
		scripts: dict[int, IScript] = {}
		warnings: list[PyMSWarning] = []
		try:
			for file in files:
				parse_context = self.get_parse_context(file)
				new_scripts = IScriptBIN.IScriptBIN.compile(parse_context)
				for new_script in new_scripts:
					# TODO: Duplicate scripts
					scripts[new_script.id] = new_script
				warnings.extend(parse_context.warnings)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		new_size = self.ibin.can_add_scripts(scripts.values())
		if new_size is not None:
			size = self.ibin.calculate_size()
			raise PyMSError('Parse', f"There is not enough room in your iscript.bin to compile these changes. The current file is {size}B out of the max 65535B, these changes would make the file {new_size}B.")
		if warnings:
			w = WarningDialog(self, warnings, True)
			if not w.cont:
				return
		self.ibin.add_scripts(scripts.values())
		self.update_iscrips_list()
		self.status.set('Import Successful!')
		self.action_states()
		self.mark_edited()

	def export(self) -> None:
		if not self.ibin:
			return
		selected_iscript_ids = self.selected_iscript_ids()
		if not selected_iscript_ids:
			return
		file_path = self.config_.last_path.txt.select_save(self)
		if not file_path:
			return
		try:
			with IO.OutputTextFile(file_path) as output:
				serialize_context = self.get_serialize_context(output)
				self.ibin.decompile(serialize_context, script_ids=selected_iscript_ids)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def listimport(self) -> None:
		if not self.is_file_open():
			return
		ImportListDialog(self, self.config_.windows.list_import, self.config_.last_path.txt, self)

	def close(self) -> None:
		if not self.is_file_open():
			return
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.iscriptlist.delete(0,END)
		self.ibin = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a BIN.')
		self.mark_edited(False)
		self.listbox_selection_changed()

	def find(self) -> None:
		if not self.is_file_open():
			return
		FindDialog(self, self, self.config_.windows.find, self.config_.find_history)

	def codeedit(self) -> None:
		selected_iscript_ids = self.selected_iscript_ids()
		CodeEditDialog(self, self, self.config_, selected_iscript_ids)

	def tblbin(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, self.config_, self, err, self.mpqhandler)

	def register_registry(self) -> None:
		try:
			register_registry('PyICE', 'bin', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyICE.md')

	def about(self) -> None:
		AboutDialog(self, 'PyICE', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()

	def get_iscript_bin(self) -> IScriptBIN.IScriptBIN:
		assert self.ibin is not None
		return self.ibin

	def get_data_context(self) -> DataContext:
		return self.data_context

	def get_serialize_context(self, output: BuiltinIO[str]) -> ICESerializeContext:
		return ICESerializeContext(output, self.data_context)

	def get_parse_context(self, input: IO.AnyInputText) -> ICEParseContext:
		with IO.InputText(input) as f:
			code = f.read()
		lexer = ICELexer(code)
		return ICEParseContext(lexer, self.data_context)
