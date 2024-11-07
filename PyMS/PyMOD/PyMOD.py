
from .Config import PyMODConfig
from .SourceFiles import *
from .CompileThread import *
from .ExtractDialog import ExtractDialog
from .SettingsUI.SettingsDialog import SettingsDialog

from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.MPQHandler import MPQHandler

LONG_VERSION = 'v%s' % Assets.version('PyMOD')

class TabID:
	files = 'files'
	logs = 'logs'

class PyMOD(MainWindow):
	def __init__(self) -> None:
		self.config_ = PyMODConfig()

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyMOD')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMOD', Assets.version('PyMOD'))
		ga.track(GAScreen('PyMOD'))
		self.minsize(400,350)
		setup_trace('PyMOD', self)
		Theme.load_theme(self.config_.theme.value, self)

		self.project_path: str | None = None
		self.source_graph: SourceFolder | None = None
		self.compile_thread: CompileThread | None = None

		self.mpqhandler = MPQHandler(self.config_.mpqs)

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.manage_settings, "Manage Settings", Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyMOD')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.notebook = Notebook(self)
		self.notebook.pack(side=TOP, padx=2, fill=BOTH, expand=1)

		frame = Frame(self.notebook)
		self.files_tree = TreeList(frame)
		self.files_tree.pack(padx=3, pady=3, fill=BOTH, expand=1)
		self.notebook.add_tab(frame, 'Files', TabID.files)

		frame = Frame(self.notebook)
		self.logs_textview = ScrolledText(frame)
		self.logs_textview.set_read_only(True)
		self.logs_textview.textview.tag_configure('error', foreground=Theme.get_color('log', 'error', default='#FF0000'))
		self.logs_textview.textview.tag_configure('warning', foreground=Theme.get_color('log', 'warning', default='#FFA500'))
		self.logs_textview.textview.tag_configure('success', foreground=Theme.get_color('log', 'success', default='#00FF00'))
		self.logs_textview.pack(padx=3, pady=3, fill=BOTH, expand=1)
		self.notebook.add_tab(frame, 'Logs', TabID.logs)

		frame = Frame(self)
		self.extract_button = Button(frame, text='Extract', command=self.extract, state=DISABLED)
		self.extract_button.pack(side=LEFT, padx=(0,10))
		self.compile_button = Button(frame, text='Compile', command=self.compile, state=DISABLED)
		self.compile_button.pack(side=LEFT)
		self.cancel_button = Button(frame, text='Cancel', command=self.cancel, state=DISABLED)
		self.cancel_button.pack(side=LEFT)
		frame.pack(side=TOP, pady=5)

		#Statusbar
		self.status = StringVar()
		self.status.set('Open or create a Mod Project.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.config_.windows.main.load_size(self)

	def initialize(self) -> None:
		UpdateDialog.check_update(self, 'PyMOD')

	def update_title(self) -> None:
		project_path = self.project_path
		if not project_path:
			project_path = 'Untitled.txt'
		if not project_path:
			self.title('PyMOD %s' % LONG_VERSION)
		else:
			self.title('PyMOD %s (%s)' % (LONG_VERSION, project_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def update_states(self) -> None:
		is_project_open = not not self.project_path
		is_compiling = not not self.compile_thread
		self.toolbar.tag_enabled('file_open', is_project_open)
		self.extract_button['state'] = NORMAL if is_project_open and not is_compiling else DISABLED
		self.compile_button['state'] = NORMAL if is_project_open and not is_compiling else DISABLED
		self.cancel_button['state'] = NORMAL if is_compiling else DISABLED

	def refresh_files(self) -> None:
		self.files_tree.delete(ALL)
		if not self.project_path:
			return
		self.source_graph = build_source_graph(self.project_path)
		self.files_tree.build(((self.source_graph, True),), lambda node: () if isinstance(node, SourceFile) else tuple((file,None) for file in node.files) + tuple((folder,True) for folder in node.folders), lambda node: node.display_name())

	def new(self) -> None:
		pass

	def open(self, project_path: str | None = None) -> None:
		if not project_path:
			project_path = self.config_.last_path.project.select_open(self)
		if not project_path:
			return
		self.close()
		self.project_path = project_path
		self.refresh_files()
		self.update_states()

	def save(self) -> None:
		pass

	def saveas(self) -> None:
		pass

	def close(self) -> None:
		pass

	def extract(self) -> None:
		ExtractDialog(self, self.mpqhandler, self.config_)

	def compile(self) -> None:
		if self.project_path is None or self.source_graph is None:
			return
		if self.compile_thread is not None:
			return
		self.refresh_files()
		self.notebook.display(TabID.logs)
		self.logs_textview.delete('1.0', END)
		self.compile_thread = CompileThread(self.project_path, self.source_graph)
		self.compile_thread.start()
		self.update_states()
		self.watch_compile()

	def cancel(self) -> None:
		if not self.compile_thread:
			return
		self.compile_thread.input_queue.put(CompileThread.InputMessage.Abort())

	def watch_compile(self) -> None:
		if self.compile_thread is None:
			return
		while True:
			try:
				message = self.compile_thread.output_queue.get(False)
			except:
				break
			if isinstance(message, CompileThread.OutputMessage.Log):
				self.logs_textview.insert(END, message.text + '\n', message.tag)
				self.logs_textview.textview.see(END)
			self.compile_thread.output_queue.task_done()
		if not self.compile_thread.is_alive():
			self.compile_thread = None
			self.update_states()
		if not self.compile_thread:
			return
		self.after(200, self.watch_compile)

	def manage_settings(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyMOD.md')

	def about(self) -> None:
		AboutDialog(self, 'PyMOD', LONG_VERSION)

	def exit(self) -> None:
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
