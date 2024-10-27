#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyAI')

def main(): # type: () -> None
	from PyMS.PyAI.PyAI import PyAI, LONG_VERSION

	from PyMS.FileFormats.AIBIN import AIBIN
	from PyMS.FileFormats.AIBIN.CodeHandlers.DataContext import DataContext
	from PyMS.FileFormats.AIBIN.CodeHandlers.AIDefinitionsHandler import AIDefinitionsHandler
	from PyMS.FileFormats.AIBIN.CodeHandlers.AISourceCodeHandlers import AIDefsSourceCodeHandler
	from PyMS.FileFormats.AIBIN.CodeHandlers.AILexer import AILexer
	from PyMS.FileFormats.AIBIN.CodeHandlers.AISerializeContext import AISerializeContext
	from PyMS.FileFormats.AIBIN.CodeHandlers.AIParseContext import AIParseContext

	from PyMS.FileFormats import DAT
	from PyMS.FileFormats import TBL

	from PyMS.Utilities import Assets
	from PyMS.Utilities.PyMSError import PyMSError
	from PyMS.Utilities import IO
	from PyMS.Utilities.CodeHandlers import Formatters

	import os, optparse, sys
	from dataclasses import dataclass

	@dataclass
	class Options(optparse.Values):
		decompile = True
		units = Assets.mpq_file_path('arr', 'units.dat')
		upgrades = Assets.mpq_file_path('arr', 'upgrades.dat')
		techdata = Assets.mpq_file_path('arr', 'techdata.dat')
		stattxt = Assets.mpq_file_path('rez', 'stat_txt.tbl')
		scripts = None # type: str | None
		aiscript = None # type: str | None
		bwscript = None # type: str | None
		hidewarns = False
		deffile = None # type: str | None
		gui = None # type: str | None

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyai.py','pyai.pyw','pyai.exe']):
		gui = PyAI()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyAI [options] <inp|aiscriptin bwscriptin> [out|aiscriptout bwscriptout]', version='PyAI %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='decompile', help="Decompile AI's from aiscript.bin and/or bwscript.bin [default]")
		p.add_option('-c', '--compile', action='store_false', dest='decompile', help="Compile AI's to an aiscript.bin and/or bwscript.bin")
		p.add_option('-u', '--units', help="Specify your own units.dat file for unit data lookups [default: PyMS\\MPQ\\arr\\units.dat]")
		p.add_option('-g', '--upgrades', help="Specify your own upgrades.dat file for upgrade data lookups [default: PyMS\\MPQ\\arr\\upgrades.dat]")
		p.add_option('-t', '--techdata', help="Specify your own techdata.dat file for technology data lookups [default: PyMS\\MPQ\\arr\\techdata.dat]")
		p.add_option('-s', '--scripts', help="A list of AI Script ID's to decompile (seperated by commas) [default: All]")
		p.add_option('-a', '--aiscript', help="Used to signify the base aiscript.bin file to compile on top of")
		p.add_option('-b', '--bwscript', help="Used to signify the base bwscript.bin file to compile on top of (aiscript required if bwscript is used)")
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: PyMS\\MPQ\\rez\\stat_txt.tbl]")
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]")
		p.add_option('-f', '--deffile', help="Specify an External Definition file containing variables to be used when interpreting/decompiling [default: None]")
		p.add_option('--gui', help="Opens a file with the GUI")
		opt = Options()
		_, args = p.parse_args(values=opt)
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
				if opt.decompile:
					if len(args) < 2:
						p.error('Invalid amount of arguments, missing bwscript.bin')
					args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'txt'))
				else:
					if len(args) < 2:
						args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
					args.append('%s%s%s' % (os.path.join(path,'bw' + os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
			warnings = []
			try:
				print("Loading units.dat '%s'..." % opt.units)
				unitsdat = DAT.UnitsDAT()
				unitsdat.load_file(opt.units)
				print("- Loading finished successfully\nLoading upgrades.dat '%s'..." % opt.upgrades)
				upgradesdat = DAT.UpgradesDAT()
				upgradesdat.load_file(opt.upgrades)
				print("- Loading finished successfully\nLoading techdata.dat '%s'..." % opt.techdata)
				techdat = DAT.TechDAT()
				techdat.load_file(opt.techdata)
				print("- Loading finished successfully\nLoading stat_txt.tbl '%s'..." % opt.stattxt)
				tbl = TBL.TBL()
				tbl.load_file(opt.stattxt)
				print('- Loading finished successfully')
				data_context = DataContext(stattxt_tbl=tbl, units_dat=unitsdat, upgrades_dat=upgradesdat, techdata_dat=techdat)
				definitions_handler = AIDefinitionsHandler()
				if opt.deffile:
					print("Loading external definitions file '%s'..." % opt.deffile)
					handler = AIDefsSourceCodeHandler()
					with IO.InputText(opt.deffile) as f:
						code = f.read()
					lexer = AILexer(code)
					parse_context = AIParseContext(lexer, definitions_handler, data_context)
					handler.parse(parse_context)
					parse_context.finalize()
					print('- Loading finished successfully')
				if opt.decompile:
					ids = None # type: list[str] | None
					if opt.scripts:
						ids = []
						for i in opt.scripts.split(','):
							if len(i) != 4:
								print('Invalid ID: %s' % i)
								return
							ids.append(i)
					bin = AIBIN.AIBIN()
					print("Loading aiscript.bin '%s' and bwscript.bin '%s'..." % (args[0], args[1]))
					bin.load(args[0], args[1])
					print(" - Loading finished successfully\nWriting AI Scripts to '%s'..." % args[2])
					# TODO: Customize formatters
					formatters = Formatters.Formatters(
						block = Formatters.HyphenBlockFormatter(),
						command = Formatters.ParensCommandFormatter(),
						comment = Formatters.HashCommentFormatter(),
					)
					with open(args[2], 'w') as f:
						serialize_context = AISerializeContext(f, definitions_handler, formatters, data_context)
						bin.decompile(serialize_context, ids)
					print(" - '%s' written succesfully" % args[2])
				else:
					bin = AIBIN.AIBIN()
					if opt.aiscript:
						if opt.bwscript:
							print("Loading base aiscript.bin '%s' and bwscript.bin '%s'..." % (os.path.abspath(opt.aiscript), os.path.abspath(opt.bwscript)))
						else:
							print("Loading base aiscript.bin '%s'..." % os.path.abspath(opt.aiscript))
						bin.load(opt.aiscript, opt.bwscript)
					print(" - Loading finished successfully\nLoading script '%s'..." % args[0])
					with IO.InputText(args[0]) as f:
						code = f.read()
					print(" - Loading finished successfully\nCompiling script '%s'..." % args[0])
					lexer = AILexer(code)
					parse_context = AIParseContext(lexer, definitions_handler, data_context)
					bin.compile(parse_context)
					warnings = parse_context.warnings
					print(" - '%s' compiled successfully\nSaving file '%s' to aiscript.bin '%s' and bwscript.bin '%s'..." % (args[0], args[0], args[1], args[2]))
					bin.save(args[1], args[2])
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
