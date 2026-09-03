
from .Config import PyMODConfig
from .Project import Project
from . import Extractor

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

import os, re

from typing import Protocol

class ExtractDialogDelegate(Protocol):
	def refresh_files(self) -> None:
		...

class ExtractDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, *, delegate: ExtractDialogDelegate, mpqhandler: MPQHandler, project: Project, config: PyMODConfig) -> None:
		self.delegate = delegate
		self.mpqhandler = mpqhandler
		self.project = project
		self.extracted_any = False
		self.search = UI.StringVar()
		self.search.set('*')
		self.search.trace_add('write', self.updatesearch)
		self.config_ = config
		self.search_history = UI.InputHistory(config=config.extract.history)
		self.regex = UI.IntVar()
		self.regex.set(0)
		self.files: list[str] = []
		self.resettimer: str | None = None
		self.searchtimer: str | None = None
		PyMSDialog.__init__(self, parent, 'Extract')

	def widgetize(self) -> UI.Widget:
		self.listbox = UI.ScrolledListbox(self, width=35, height=10)
		self.listbox.pack(fill=UI.BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()

		frame = UI.Frame(self)
		self.textdrop = UI.TextDropDown(frame, self.search, self.search_history)
		self.textdrop_entry_c = self.textdrop.entry['bg']
		self.textdrop.pack(side=UI.LEFT, fill=UI.X, padx=1, pady=2)
		UI.Radiobutton(frame, text='Wildcard', variable=self.regex, value=0, command=self.updatelist).pack(side=UI.LEFT, padx=1, pady=2)
		UI.Radiobutton(frame, text='Regex', variable=self.regex, value=1, command=self.updatelist).pack(side=UI.LEFT, padx=1, pady=2)
		frame.pack(fill=UI.X)

		frame = UI.Frame(self)
		self.extract_button = UI.Button(frame, text='Extract', width=10, command=self.extract)
		self.extract_button.pack(side=UI.LEFT, padx=1, pady=3)
		UI.Button(frame, text='Done', width=10, command=self.cancel).pack(side=UI.LEFT, padx=1, pady=3)
		frame.pack(side=UI.BOTTOM)

		self.listfiles()

		return self.extract_button

	def setup_complete(self) -> None:
		self.config_.windows.extract.load_size(self)

	def listfiles(self) -> None:
		def get_files_list(mpqhandler: MPQHandler) -> list[str]:
			files: list[str] = []
			for file_entry in mpqhandler.list_files():
				file_name = file_entry.file_name.decode('utf-8')
				if not file_name in files:
					files.append(file_name)
			for path,_,filenames in os.walk(Assets.mpq_dir):
				for filename in filenames:
					mpq_filename = Assets.mpq_file_path_to_file_name(os.path.join(path, filename))
					if not mpq_filename in files:
						files.append(mpq_filename)
			files.sort()
			return files
		def update_files_list(files: list[str] | Exception | None) -> None:
			if not isinstance(files, list):
				error: PyMSError
				if isinstance(files, PyMSError):
					error = files
				elif isinstance(files, Exception):
					error = PyMSError('Extract', "Couldn't list MPQ files", cause=files)
				else:
					error = PyMSError('Extract', "Couldn't list MPQ files")
				ErrorDialog(self, error)
				return
			self.files = files
			self.updatelist()
		self.after_background(update_files_list, get_files_list, self.mpqhandler)

	def updatelist(self) -> None:
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
			self.searchtimer = None
		self.listbox.delete(0,UI.END)
		s = self.search.get()
		if not self.regex.get():
			s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
		try:
			r = re.compile(s)
		except Exception:
			self.resettimer = self.after(1000, self.updatecolor)
			self.textdrop.entry['bg'] = '#FFB4B4'
		else:
			for f in filter(r.match, self.files):
				self.listbox.insert(UI.END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.extract_button['state'] = UI.NORMAL
		else:
			self.extract_button['state'] = UI.DISABLED

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop_entry_c

	def updatesearch(self, *_) -> None:
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def selected_file(self) -> str | None:
		selection = self.listbox.curselection()
		if not selection:
			return None
		return self.listbox.get(int(selection[0]))

	def extract(self) -> None:
		mpq_file_name = self.selected_file()
		if not mpq_file_name:
			return
		extractor_type = Extractor.find_extractor(mpq_file_name)
		extractor = extractor_type(self, mpqhandler=self.mpqhandler, project=self.project, config=self.config_, mpq_file_name=mpq_file_name)
		if extractor.extracted:
			self.extracted_any = True

	def dismiss(self) -> None:
		self.config_.windows.extract.save_size(self)
		# Refreshing on dismiss rather than after each extract keeps the source graph from being
		# rebuilt once per file while a bunch of files are pulled out in a row
		if self.extracted_any:
			self.delegate.refresh_files()
		PyMSDialog.dismiss(self)
