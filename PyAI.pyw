#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyAI')

def main():
	from PyMS.PyAI.PyAI import PyAI, LONG_VERSION

	from PyMS.FileFormats import AIBIN

	from PyMS.Utilities import Assets
	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyai.py','pyai.pyw','pyai.exe']):
		gui = PyAI()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyAI [options] <inp|aiscriptin bwscriptin> [out|aiscriptout bwscriptout]', version='PyAI %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile AI's from aiscript.bin and/or bwscript.bin [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile AI's to an aiscript.bin and/or bwscript.bin")
		p.add_option('-u', '--units', help="Specify your own units.dat file for unit data lookups [default: Libs\\MPQ\\arr\\units.dat]", default=Assets.mpq_file_path('arr', 'units.dat'))
		p.add_option('-g', '--upgrades', help="Specify your own upgrades.dat file for upgrade data lookups [default: Libs\\MPQ\\arr\\upgrades.dat]", default=Assets.mpq_file_path('arr', 'upgrades.dat'))
		p.add_option('-t', '--techdata', help="Specify your own techdata.dat file for technology data lookups [default: Libs\\MPQ\\arr\\techdata.dat]", default=Assets.mpq_file_path('arr', 'techdata.dat'))
		p.add_option('-s', '--scripts', help="A list of AI Script ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-a', '--aiscript', help="Used to signify the base aiscript.bin file to compile on top of", default='')
		p.add_option('-b', '--bwscript', help="Used to signify the base bwscript.bin file to compile on top of", default='')
		p.add_option('-l', '--longlabels', action='store_false', help="Used to signify that you want decompiled scripts to use desriptive command names [default: Off]", default=True)
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=Assets.mpq_file_path('rez', 'stat_txt.tbl'))
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for commands and parameters [default: Off]", default=False)
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]", default=False)
		p.add_option('-f', '--deffile', help="Specify an External Definition file containing variables to be used when interpreting/decompiling [default: None]", default=None)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyAI(opt.gui)
			gui.startup()
		else:
			if not len(args) in [2,3]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			if len(args) != 3:
				if opt.convert:
					if len(args) < 2:
						p.error('Invalid amount of arguments, missing bwscript.bin')
					args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'txt'))
				else:
					if len(args) < 2:
						args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
					args.append('%s%s%s' % (os.path.join(path,'bw' + os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
			warnings = []
			try:
				if opt.convert:
					if opt.scripts:
						ids = []
						for i in opt.scripts.split(','):
							if len(i) != 4:
								print('Invalid ID: %s' % ids[-1])
								return
							ids.append(i)
					else:
						ids = None
					print("Loading bwscript.bin '%s', units.dat '%s', upgrades.dat '%s', techdata.dat '%s', and stat_txt.tbl '%s'" % (args[1],opt.units,opt.upgrades,opt.techdata,opt.stattxt))
					bin = AIBIN.AIBIN(args[1],opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					warnings.extend(bin.warnings)
					print(" - Loading finished successfully\nReading BINs '%s' and '%s'..." % (args[0],args[1]))
					warnings.extend(bin.load_file(args[0]))
					print(" - BINs read successfully\nWriting AI Scripts to '%s'..." % args[2])
					warnings.extend(bin.decompile(args[2],opt.deffile,opt.reference,opt.longlabels,ids))
					print(" - '%s' written succesfully" % args[2])
				else:
					if opt.bwscript:
						print("Loading base bwscript.bin '%s', units.dat '%s', upgrades.dat '%s', techdata.dat '%s', and stat_txt.tbl '%s'" % (os.path.abspath(opt.bwscript),opt.units,opt.upgrades,opt.techdata,opt.stattxt))
						bin = AIBIN.AIBIN(os.path.abspath(opt.bwscript),opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					else:
						print("Loading units.dat '%s', upgrades.dat '%s', techdata.dat '%s', and stat_txt.tbl '%s'" % (opt.units,opt.upgrades,opt.techdata,opt.stattxt))
						bin = AIBIN.AIBIN('',opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					print(" - Loading finished successfully")
					if opt.aiscript:
						print("Loading base aiscript.bin '%s'..." % os.path.abspath(opt.aiscript))
						bin.load_file(os.path.abspath(opt.aiscript))
						print(" - aiscript.bin read successfully")
					print("Interpreting file '%s'..." % args[0])
					warnings.extend(bin.interpret(args[0],opt.deffile))
					print(" - '%s' read successfully\nCompiling file '%s' to aiscript.bin '%s' and bwscript.bin '%s'..." % (args[0], args[0], args[1], args[2]))
					bin.compile(args[1], args[2])
					print(" - aiscript.bin '%s' and bwscript.bin '%s' written succesfully" % (args[1], args[2]))
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
