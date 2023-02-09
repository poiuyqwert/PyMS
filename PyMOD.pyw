#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyMOD')

def main():
	from PyMS.PyMOD.PyMOD import PyMOD

	gui = PyMOD()
	gui.startup()

if __name__ == '__main__':
	main()
