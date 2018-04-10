# PyMS
PyMS is a cross platform BroodWar modding suite written using [Python](http://www.python.org). PyMS contains 15 programs to edit most of the file types you will encounter while modding.

## Table of Contents
1. [Installation](https://github.com/poiuyqwert/PyMS#installation)
1. [Issues](https://github.com/poiuyqwert/PyMS#issues)
1. [Programs](https://github.com/poiuyqwert/PyMS#programs)
   * [PyAI](https://github.com/poiuyqwert/PyMS#PyAI)
   * [PyBIN](https://github.com/poiuyqwert/PyMS#PyBIN)
   * [PyDAT](https://github.com/poiuyqwert/PyMS#PyDAT)
   * [PyFNT](https://github.com/poiuyqwert/PyMS#PyFNT)
   * [PyGOT](https://github.com/poiuyqwert/PyMS#PyGOT)
   * [PyGRP](https://github.com/poiuyqwert/PyMS#PyGRP)
   * [PyICE](https://github.com/poiuyqwert/PyMS#PyICE)
   * [PyLO](https://github.com/poiuyqwert/PyMS#PyLO)
   * [PyMPQ](https://github.com/poiuyqwert/PyMS#PyMPQ)
   * [PyPAL](https://github.com/poiuyqwert/PyMS#PyPAL)
   * [PyPCX](https://github.com/poiuyqwert/PyMS#PyPCX)
   * [PySPK](https://github.com/poiuyqwert/PyMS#PySPK)
   * [PyTBL](https://github.com/poiuyqwert/PyMS#PyTBL)
   * [PyTILE](https://github.com/poiuyqwert/PyMS#PyTILE)
   * [PyTRG](https://github.com/poiuyqwert/PyMS#PyTRG)


## Installation
1. **Install Python.** You should get the latest Python 2.7.x, currently that is [Python 2.7.12](https://www.python.org/downloads/release/python-2712/)
2. **Install PILLOW.** Use PIP, the Python package manager, to [install PILLOW](https://pillow.readthedocs.io/en/latest/installation.html#basic-installation) (PIL will also work)
3. **Download PyMS.** Always get the most up to date PyMS from [github](https://github.com/poiuyqwert/pyms) ([direct link](https://github.com/poiuyqwert/PyMS/archive/master.zip)). If you are updating PyMS, you can keep your settings files located in the Settings folder.

## Issues/Feedback
If you run into any issues with the programs, or have any feedback to improve the programs, please do one of the following:
1. Create an issue [here on github](https://github.com/poiuyqwert/PyMS/issues)
1. Post in [this thread](http://www.staredit.net/topic/16686/) on [StarEdit.net](http://www.staredit.net)
1. [Email me](mailto:p.q.poiuy.qwert@gmail.com)

Please include as much information as possible. If you are reporting an issue, please include:
* The version of the program you had issues with (you can check in Libs\versions.json)
* The OS you are running on
* The error message or crash logs. If the program crashed without an error dialog, you can check in the Libs\Logs\ folder for the programs log file

## Analytics
At the moment PyMS only tracks the launch of PyMS programs, anonamously and with no sensitive information sent. An example of the data sent in these analytics calls:
    {'v': '1', 'cid': 'bd32dccd-13be-4027-86eb-8a3fc11c61e7', 'av': '4.0.0', 'an': 'PyGRP', 'cd4': '10.12.6', 'cd5': 64, 'cd1': '1.2.3', 'cd2': '2.7.10', 'cd3': 'darwin', 'tid': 'UA-########-#', 'cd': 'PyGRP', 't': 'screenview'}
Even though the analytics is anonamous and as no sensitive information, you can still disable analytics by editing "Settings/PyMS.txt", and setting the "allow" key under "analytics" to be False.

## Programs
PyMS contains 16 programs to edit most of the file types you will encounter while modding.

### PyAI
PyAI is used for editing AI .bin files.

### PyBIN
PyBIN is used for editing dialog .bin files.

### PyDAT
PyDAT is used for editing the various .dat files.

### PyFNT
PyFNT is used for converting .fnt Font files to and from .bmp files.

### PyGOT
PyGOT is used for editing the Game Template .got files.

### PyGRP
PyGRP is used for editing various graphics in .grp files.

### PyICE
PyICE is used for editing the graphics animation script .bin files.

### PyLO
PyLO is used for editing the various offset .lo? files.

### PyMPQ
PyMPQ is used for editing .mpq files.

### PyPAL
PyPAL is used for editing the various image palette files (.pal, .wpe, etc.)

### PyPCX
PyPAL is used for converting .pcx files to and from .bmp files.

### PySPK
PySPK is used for editing the space paralax .spk files.

### PyTBL
PyTBL is used for editing the strings .tbl files.

### PyTILE
PyTILE is used for editing the tileset files (.cv5, .vx4, .vf4, .vr4, .dddata)

### PyTRG
PyTRG is used for editing triggers (.trg files)