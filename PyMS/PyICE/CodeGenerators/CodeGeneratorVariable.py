
from ...Utilities.UIKit import *
from ...Utilities.PyMSDialog import PyMSDialog

class CodeGeneratorVariable:
	def __init__(self, generator, name='variable'):
		self.generator = generator
		self.name = name

class CodeGeneratorVariableEditor(PyMSDialog):
	def __init__(self, parent, variable):
		self.variable = variable
		PyMSDialog.__init__(self, parent, 'Variable Editor', grabwait=True, resizable=variable.generator.EDITOR.RESIZABLE)

	def widgetize(self):
		self.name = StringVar()
		self.name.set(self.variable.name)
		def strip_name(*_):
			strip_re = re.compile(r'[^a-zA-Z0-9_]')
			name = self.name.get()
			stripped = strip_re.sub('', name)
			if stripped != name:
				self.name.set(stripped)
		self.name.trace('w', strip_name)

		Label(self, text='Name:', anchor=W).pack(side=TOP, fill=X, padx=3)
		Entry(self, textvariable=self.name).pack(side=TOP, fill=X, padx=3)

		self.editor = self.variable.generator.EDITOR(self, self.variable.generator)
		self.editor.pack(side=TOP, fill=BOTH, expand=1, padx=3, pady=3)

		buts = Frame(self)
		done = Button(buts, text='Done', command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return done

	def setup_complete(self):
		self.parent.settings.windows.generator.editor.load_window_size(self.variable.generator.TYPE, self)

	def ok(self):
		self.variable.name = self.parent.unique_name(self.name.get(), self.variable)
		self.editor.save()
		self.parent.update_list()
		PyMSDialog.ok(self)

	def dismiss(self):
		self.parent.settings.windows.generator.editor.save_window_size(self.variable.generator.TYPE, self)
		PyMSDialog.dismiss(self)
