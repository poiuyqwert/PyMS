import os

progs = []
for prog in ['PyAI','PyDAT','PyFNT','PyGOT','PyGRP','PyICE','PyTRG','PyLO','PyPAL','PyTBL','PyTILE','PyPCX','PyMPQ']:
	progs.append({"script":prog + ".pyw","icon_resources": [(1, "Images\\%s.ico" % prog)]})

def list(path, exc=[]):
	return [os.path.join(path,file) for file in os.listdir(path) if not file in exc]

data = (
	('',['unitdef.txt']),
	('Libs',['Libs\\SFmpq.dll']),
	('Libs\\Data',list('Libs\\Data')),
	('Libs\\Temp',[]),
	#('Libs\\MPQ',[]),
	('Libs\\MPQ\\arr',list('Libs\\MPQ\\arr')),
	('Libs\\MPQ\\game',list('Libs\\MPQ\\game')),
	('Libs\\MPQ\\rez',list('Libs\\MPQ\\rez')),
	('Libs\\MPQ\\scripts',list('Libs\\MPQ\\scripts')),
	('Libs\\MPQ\\font',list('Libs\\MPQ\\font')),
	('Libs\\MPQ\\unit\\thingy',list('Libs\\MPQ\\unit\\thingy')),
	('Libs\\MPQ\\unit\\cmdbtns',list('Libs\\MPQ\\unit\\cmdbtns')),
	('Images',list('Images',['Thumbs.db'])),
	('Palettes',list('Palettes')),
	('Docs',[file for file in list('Docs') if file[-4:] in ['.css','html']]),
	('Settings',[]),
)

from distutils.core import setup
import py2exe
setup(
	windows = progs,
	author="poiuy_qwert",
	author_email="p.q.poiuy.qwert@gmail.com",
	url="http://www.broodwarai.com/index.php?page=pyms",
	zipfile=os.path.join('Libs','Libs.zip'),
	data_files=data,
	options={'py2exe':{
		'excludes':['_ssl','difflib','doctest','locale','pickle','calendar','email']
	}}
)