#!/usr/bin/env python

from PyMS.Utilities.Compatability import check_compat
check_compat('PyICE')

def main():
	from PyMS.PyICE.PyICE import PyICE, LONG_VERSION

	from PyMS.FileFormats import IScriptBIN

	from PyMS.Utilities import Assets
	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyice.py','pyice.pyw','pyice.exe']):
		gui = PyICE()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyICE [options] <inp|iscriptin> [out|iscriptout]', version='PyICE %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile iscripts from iscript.bin [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile iscripts to an iscript.bin")
		p.add_option('-a', '--weapons', help="Specify your own weapons.dat file for weapon data lookups [default: Libs\\MPQ\\arr\\weapons.dat]", default=Assets.mpq_file_path('arr', 'weapons.dat'))
		p.add_option('-l', '--flingy', help="Specify your own flingy.dat file for flingy data lookups [default: Libs\\MPQ\\arr\\flingy.dat]", default=Assets.mpq_file_path('arr', 'flingy.dat'))
		p.add_option('-i', '--images', help="Specify your own images.dat file for image data lookups [default: Libs\\MPQ\\arr\\images.dat]", default=Assets.mpq_file_path('arr', 'images.dat'))
		p.add_option('-p', '--sprites', help="Specify your own sprites.dat file for sprite data lookups [default: Libs\\MPQ\\arr\\sprite.dat]", default=Assets.mpq_file_path('arr', 'sprites.dat'))
		p.add_option('-f', '--sfxdata', help="Specify your own sfxdata.dat file for sound data lookups [default: Libs\\MPQ\\arr\\sfxdata.dat]", default=Assets.mpq_file_path('arr', 'sfxdata.dat'))
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=Assets.mpq_file_path('rez','stat_txt.tbl'))
		p.add_option('-m', '--imagestbl', help="Used to signify the images.tbl file to use [default: Libs\\MPQ\\arr\\images.tbl]", default=Assets.mpq_file_path('arr', 'images.tbl'))
		p.add_option('-t', '--sfxdatatbl', help="Used to signify the sfxdata.tbl file to use [default: Libs\\MPQ\\arr\\sfxdata.tbl]", default=Assets.mpq_file_path('arr', 'sfxdata.tbl'))
		p.add_option('-s', '--scripts', help="A list of iscript ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-b', '--iscript', help="Used to signify the base iscript.bin file to compile on top of", default='')
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for commands and parameters [default: Off]", default=False)
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyICE(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'bin'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			warnings = []
			try:
				if opt.convert:
					if opt.scripts:
						ids = []
						for i in opt.scripts.split(','):
							ids.append(i)
					else:
						ids = None
					print("Loading weapons.dat '%s', flingy.dat '%s', images.dat '%s', sprites.dat '%s', sdxdata.dat '%s', stat_txt.tbl '%s', images.tbl '%s', and sfxdata.tbl '%s'" % (opt.weapons,opt.flingy,opt.sprites,opt.images,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl))
					ibin = IScriptBIN.IScriptBIN(opt.weapons,opt.flingy,opt.images,opt.sprites,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					print(" - Loading finished successfully\nReading BIN '%s'..." % args[0])
					ibin.load_file(args[0])
					print(" - BIN read successfully\nWriting iscript entries to '%s'..." % args[1])
					ibin.decompile(args[1],opt.reference,ids)
					print(" - '%s' written succesfully" % args[1])
				else:
					print("Loading weapons.dat '%s', flingy.dat '%s', images.dat '%s', sprites.dat '%s', sdxdata.dat '%s', stat_txt.tbl '%s', images.tbl '%s', and sfxdata.tbl '%s'" % (opt.weapons,opt.flingy,opt.sprites,opt.images,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl))
					ibin = IScriptBIN.IScriptBIN(opt.weapons,opt.flingy,opt.images,opt.sprites,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					print(" - Loading finished successfully")
					if opt.iscript:
						print("Loading base iscript.bin '%s'..." % os.path.abspath(opt.iscript))
						ibin.load_file(os.path.abspath(opt.iscript))
						print(" - iscript.bin read successfully")
					print("Interpreting file '%s'..." % args[0])
					warnings.extend(ibin.interpret(args[0]))
					print(" - '%s' read successfully\nCompiling file '%s' to iscript.bin '%s'..." % (args[0], args[0], args[1]))
					ibin.compile(args[1])
					print(" - iscript.bin '%s' written succesfully" % args[1])
				if not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
			except PyMSError as e:
				if warnings and not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
				print(repr(e))

if __name__ == '__main__':
	main()