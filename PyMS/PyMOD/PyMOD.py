
from .Config import PyMODConfig
from . import Source
from .CompileThread import CompileThread, CompileResult
from .ExtractDialog import ExtractDialog
from .SettingsUI.SettingsDialog import SettingsDialog
from .Project import Project
from .NameDialog import NameDialog

from ..Utilities import UIKit as UI
from ..Utilities import Assets
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

import os, shutil

LONG_VERSION = f"v{Assets.version('PyMOD')}"

class TabID:
	files = 'files'
	logs = 'logs'

class PyMOD(UI.MainWindow):
	def __init__(self, open_path: str | None = None) -> None:
		self.config_ = PyMODConfig()

		#Window
		UI.MainWindow.__init__(self)
		self.set_icon('PyMOD')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMOD', Assets.version('PyMOD'))
		ga.track(GAScreen('PyMOD'))
		self.minsize(400,350)
		setup_trace('PyMOD', self)
		UI.Theme.load_theme(self.config_.theme.value, self)

		self.project: Project | None = None
		self.compile_thread: CompileThread | None = None
		self.compile_result: CompileResult | None = None

		self.mpqhandler = MPQHandler(self.config_.settings.mpqs)

		self.update_title()

		#Toolbar
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n, tags='not_compiling')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o, tags='not_compiling')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, enabled=False, tags=('file_open', 'not_compiling'))
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.manage_settings, "Manage Settings", UI.Ctrl.m, tags='not_compiling')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', UI.Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyMOD')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		self.notebook = UI.Notebook(self)
		self.notebook.pack(side=UI.TOP, padx=2, fill=UI.BOTH, expand=1)

		frame = UI.Frame(self.notebook)
		self.files_tree = UI.TreeList(frame)
		self.files_tree.pack(padx=3, pady=3, fill=UI.BOTH, expand=1)
		self.refresh_button = UI.Button(frame, text='Refresh', command=self.refresh_files, state=UI.DISABLED)
		self.refresh_button.pack(side=UI.BOTTOM, pady=(5, 0))
		self.notebook.add_tab(frame, 'Files', TabID.files)

		frame = UI.Frame(self.notebook)
		self.logs_textview = UI.ScrolledText(frame)
		self.logs_textview.set_read_only(True)
		self.logs_textview.textview.tag_configure('error', foreground=UI.Theme.get_color('log', 'error', default='#FF0000'))
		self.logs_textview.textview.tag_configure('warning', foreground=UI.Theme.get_color('log', 'warning', default='#FFA500'))
		self.logs_textview.textview.tag_configure('success', foreground=UI.Theme.get_color('log', 'success', default='#00FF00'))
		self.logs_textview.pack(padx=3, pady=3, fill=UI.BOTH, expand=1)
		self.notebook.add_tab(frame, 'Logs', TabID.logs)

		frame = UI.Frame(self)
		self.extract_button = UI.Button(frame, text='Extract', command=self.extract, state=UI.DISABLED)
		self.extract_button.pack(side=UI.LEFT, padx=(0,10))
		self.compile_button = UI.Button(frame, text='Compile', command=self.compile, state=UI.DISABLED)
		self.compile_button.pack(side=UI.LEFT)
		self.clean_button = UI.Button(frame, text='Clean', command=self.clean, state=UI.DISABLED)
		self.clean_button.pack(side=UI.LEFT)
		self.cancel_button = UI.Button(frame, text='Cancel', command=self.cancel, state=UI.DISABLED)
		self.cancel_button.pack(side=UI.LEFT)
		frame.pack(side=UI.TOP, pady=5)

		#Statusbar
		self.status = UI.StringVar()
		self.status.set('Open or create a Mod Project.')
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, width=35)
		statusbar.add_spacer()
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.update_states()

		self.config_.windows.main.load_size(self)

		if open_path:
			self.open(open_path)

	def initialize(self) -> None:
		UpdateDialog.check_update(self, 'PyMOD')

	def update_title(self) -> None:
		if not self.project:
			self.title(f'PyMOD {LONG_VERSION}')
		else:
			self.title(f'PyMOD {LONG_VERSION} ({self.project.path})')

	def update_states(self) -> None:
		is_project_open = not not self.project
		is_compiling = not not self.compile_thread
		self.toolbar.tag_enabled('file_open', is_project_open)
		self.toolbar.tag_enabled('not_compiling', not is_compiling)
		self.refresh_button['state'] = UI.NORMAL if is_project_open and not is_compiling else UI.DISABLED
		self.extract_button['state'] = UI.NORMAL if is_project_open and not is_compiling else UI.DISABLED
		self.compile_button['state'] = UI.NORMAL if is_project_open and not is_compiling else UI.DISABLED
		self.clean_button['state'] = UI.NORMAL if is_project_open and not is_compiling else UI.DISABLED
		self.cancel_button['state'] = UI.NORMAL if is_compiling else UI.DISABLED

	def refresh_files(self) -> None:
		self.files_tree.delete(UI.ALL)
		if not self.project:
			return
		if source_graph := self.project.update_source_graph():
			self.files_tree.build(((source_graph, True),), lambda node: tuple((item,None if isinstance(item, Source.File) else True) for item in node.children) if isinstance(node, Source.Folder) else (), lambda node: node.display_name())
		else:
			self.files_tree.delete(UI.ALL)

	def new(self) -> None:
		parent_path = self.config_.last_path.project.select_open(self, title='Select Containing Folder')
		if not parent_path:
			return
		project_name = NameDialog(self, parent_path, self.config_.windows.name).name
		if not project_name:
			return
		project_path = os.path.join(parent_path, project_name)
		if os.path.exists(project_path):
			ErrorDialog(self, PyMSError('New', f"Couldn't create project, `{project_path}` already exists"))
			return
		project = Project(project_path)
		try:
			project.new()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.open_project(project)

	def open(self, project_path: str | None = None) -> None:
		if not project_path:
			project_path = self.config_.last_path.project.select_open(self)
		if not project_path:
			return
		project = Project(project_path)
		try:
			project.load()
		except PyMSError:
			if not UI.MessageBox.askyesno(parent=self, title='Initialize Project?', message=f'`{project_path}` is not a PyMOD project. Initialize it as one?'):
				return
			try:
				project.new()
			except PyMSError as e:
				ErrorDialog(self, e)
				return
		self.open_project(project)

	def open_project(self, project: Project) -> None:
		self.close()
		self.project = project
		self.status.set(f'Project `{os.path.basename(project.path)}` opened.')
		self.update_title()
		self.refresh_files()
		self.update_states()

	def close(self) -> None:
		self.project = None
		self.status.set('Open or create a Mod Project.')
		self.update_title()
		self.refresh_files()
		self.update_states()

	def extract(self) -> None:
		ExtractDialog(self, self.mpqhandler, self.config_)

	def compile(self) -> None:
		if self.project is None:
			return
		if self.compile_thread is not None:
			return
		self.refresh_files()
		if not self.project.source_graph:
			self.status.set('No source files to compile.')
			return
		self.notebook.display(TabID.logs)
		self.logs_textview.delete('1.0', UI.END)
		self.compile_result = None
		self.compile_thread = CompileThread(self.project)
		self.compile_thread.start()
		self.status.set('Compiling...')
		self.update_states()
		self.watch_compile()

	def clean(self) -> None:
		if self.project is None:
			return
		self.notebook.display(TabID.logs)
		self.logs_textview.delete('1.0', UI.END)
		self.logs_textview.insert(UI.END, f'Cleaning intermediates folder `{self.project.intermediates_path}`...')
		if not os.path.exists(self.project.intermediates_path):
			self.logs_textview.insert(UI.END, "\n  Folder doesn't exist, no cleanup required")
			return
		try:
			shutil.rmtree(self.project.intermediates_path)
		except Exception as e:
			self.logs_textview.insert(UI.END, f"\n  Couldn't clean intermediates folder: {e}", 'error')
			self.status.set('Clean failed.')
			return
		self.logs_textview.insert(UI.END, '\n  Clean complete!', 'success')
		self.status.set('Clean complete.')

	def cancel(self) -> None:
		if not self.compile_thread:
			return
		self.compile_thread.input_queue.put(CompileThread.InputMessage.Abort())

	def watch_compile(self) -> None:
		if self.compile_thread is None:
			return
		# Capture liveness before draining, so a thread that logs its final messages and exits
		# mid-drain gets one more pass before being considered finished
		was_alive = self.compile_thread.is_alive()
		while True:
			try:
				message = self.compile_thread.output_queue.get(False)
			except Exception:
				break
			if isinstance(message, CompileThread.OutputMessage.Log):
				self.logs_textview.insert(UI.END, message.text + '\n', message.tag)
				self.logs_textview.textview.see(UI.END)
			elif isinstance(message, CompileThread.OutputMessage.Done):
				self.compile_result = message.result
			self.compile_thread.output_queue.task_done()
		if not was_alive:
			self.compile_thread = None
			match self.compile_result:
				case CompileResult.failure:
					self.status.set('Compile failed.')
				case CompileResult.aborted:
					self.status.set('Compile aborted.')
				case _:
					self.status.set('Compile finished.')
			self.update_states()
			return
		self.after(200, self.watch_compile)

	def manage_settings(self) -> None:
		SettingsDialog(self, self.config_, self.mpqhandler)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyMOD.md')

	def about(self) -> None:
		AboutDialog(self, 'PyMOD', LONG_VERSION)

	def exit(self) -> None:
		if self.compile_thread is not None and self.compile_thread.is_alive():
			if not UI.MessageBox.askyesno(parent=self, title='Compile in Progress', message='A compile is in progress. Cancel the compile and exit?'):
				return
			self.compile_thread.input_queue.put(CompileThread.InputMessage.Abort())
			self.compile_thread.join()
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
