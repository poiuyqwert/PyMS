
from ..FileFormats import TBL

from ..Utilities.utils import fit
from ..Utilities.UIKit import *
from ..Utilities.Tooltip import Tooltip

class ListboxTooltip(Tooltip):
	def __init__(self, parent, font=None, delay=750, press=False):
		if font == None:
			font = Font.fixed()
		Tooltip.__init__(self, parent, '', font, delay, press)
		self.index = None

	def enter(self, e):
		if self.parent.size():
			self.motion(e)
			Tooltip.enter(self,e)

	def leave(self, e=None):
		Tooltip.leave(self,e)
		if e and e.type == '4':
			self.enter(e)

	def motion(self, e):
		if self.tip and self.index != self.parent.nearest(e.y):
			self.leave()
			self.enter(e)
		self.pos = (e.x,e.y)
		Tooltip.motion(self, e)

	def showtip(self):
		if self.tip:
			return
		self.tip = Toplevel(self.parent)
		self.tip.maxsize(640,400)
		self.tip.wm_overrideredirect(1)
		pos = list(self.parent.winfo_pointerxy())
		self.index = self.parent.nearest(pos[1] - self.parent.winfo_rooty())
		item = self.parent.get_entry(self.index)
		id = item[0]
		flags = ''
		comma = False
		for d,f in zip(['BroodWar Only','Invisible in StarEdit','Requires a Location'],item[2]):
			if f == '1':
				if comma:
					flags += ', '
				else:
					comma = True
				if not flags:
					flags = 'Flags             : '
				flags += d
		if flags:
			flags += '\n'
		text = "Script ID         : %s\nIn bwscript.bin   : %s\n%sString ID         : %s\n" % (id, ['No','Yes'][item[1]], flags, item[3])
		ai = self.parent.master.ai
		text += fit('String            : ', TBL.decompile_string(ai.tbl.strings[ai.ais[id][1]]), end=True)
		if id in ai.aiinfo and ai.aiinfo[id][0]:
			text += 'Extra Information : %s' % ai.aiinfo[id][0].replace('\n','\n                    ')
		else:
			text = text[:-1]
		frame = Frame(self.tip, background='#FFFFC8', relief=SOLID, borderwidth=1)
		Label(frame, text=text, justify=LEFT, font=self.font, fg='#000', background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
		frame.pack()
		self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		self.tip.update_idletasks()
		move = False
		if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
			move = True
			pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
		if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
			move = True
			pos[1] -= self.tip.winfo_reqheight() + 44
		if move:
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
