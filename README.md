# PyMS
PyMS is a cross platform BroodWar modding suite written using [Python](http://www.python.org). PyMS contains 15 programs to edit most of the file types you will encounter while modding.

## Table of Contents
1. [Installation](https://github.com/poiuyqwert/PyMS#installation)
1. [Issues](https://github.com/poiuyqwert/PyMS#issues)
1. [Analytics](https://github.com/poiuyqwert/PyMS#analytics)
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
   
   **Note:** On Windows, you must ensure that Python is in your "Path" environment variable. If you use the MSI Installer there is an "Add Python.exe to path" option you should make sure is enabled during installation, otherwise you can [set it up manually](https://docs.python.org/2.7/using/windows.html#excursus-setting-environment-variables).
2. **Install Dependencies.** Use PIP (the Python package manager), to install all dependencies of PyMS by opening the command line, navigating to the PyMS folder, and running `python2.7 -m pip install -r requirements.txt`
3. **Download PyMS.** Always get the most up to date PyMS from [github](https://github.com/poiuyqwert/pyms) ([direct link](https://github.com/poiuyqwert/PyMS/archive/master.zip)). If you are updating PyMS, you can keep your settings files located in the Settings folder.

## Issues/Feedback
If you run into any issues with the programs, or have any feedback to improve the programs, please do one of the following:
1. Create an issue [here on github](https://github.com/poiuyqwert/PyMS/issues)
1. Post in [this thread](http://www.staredit.net/topic/17719/) on [StarEdit.net](http://www.staredit.net)
1. [Email me](mailto:p.q.poiuy.qwert@gmail.com)

Please include as much information as possible. If you are reporting an issue, please include:
* The version of the program you had issues with (you can check in Libs\versions.json)
* The OS you are running on
* The error message or crash logs. If the program crashed without an error dialog, you can check in the Libs\Logs\ folder for the programs log file

## Analytics
At the moment PyMS only tracks the launch of PyMS programs, anonamously and with no sensitive information sent. An example of the data sent in these analytics calls:

```
{
  "an": "PyGRP",
  "av": "4.0.0",
  "cd": "PyGRP",
  "cd1": "1.2.3",
  "cd2": "2.7.10",
  "cd3": "darwin",
  "cd4": "10.12.6",
  "cd5": 64,
  "cid": "bd32dccd-13be-4027-86eb-8a3fc11c61e7",
  "t": "screenview",
  "tid": "UA-########-#",
  "v": "1"
}
```

Even though the analytics is anonamous and has no sensitive information, you can still disable analytics by editing "Settings/PyMS.txt", and setting the "allow" key under "analytics" to be False.

## Programs
PyMS contains 16 programs to edit most of the file types you will encounter while modding.

### PyAI
[PyAI](/Help/Programs/PyAI.md) is used for editing AI [.bin](/Help/Files/aiscript.bin.md) files.

### PyBIN
[PyBIN](/Help/Programs/PyBIN.md) is used for editing dialog [.bin](/Help/Files/UI_BIN.md) files.

### PyDAT
[PyDAT](/Help/Programs/PyDAT.md) is used for editing the various [.dat](/Help/Files/DAT/units.dat.md) files.

### PyFNT
[PyFNT](/Help/Programs/PyFNT.md) is used for converting [.fnt](/Help/Files/FNT.md) Font files to and from [.bmp](/Help/Files/BMP.md) files.

### PyGOT
[PyGOT](/Help/Programs/PyGOT.md) is used for editing the Game Template [.got](/Help/Files/GOT.md) files.

### PyGRP
[PyGRP](/Help/Programs/PyGRP.md) is used for editing various graphics in [.grp](/Help/Files/GRP.md) files.

### PyICE
[PyICE](/Help/Programs/PyICE.md) is used for editing the graphics animation script [.bin](/Help/Files/iscript.bin.md) files.

### PyLO
[PyLO](/Help/Programs/PyLO.md) is used for editing the various offset [.lo?](/Help/Files/LO.md) files.

### PyMPQ
[PyMPQ](/Help/Programs/PyMPQ.md) is used for editing [.mpq](/Help/Files/MPQ.md) files.

### PyPAL
[PyPAL](/Help/Programs/PyPAL.md) is used for editing the various image [palette](/Help/Files/Palettes.md) files (.pal, .wpe, etc.)

### PyPCX
[PyPAL](/Help/Programs/PyPAL.md) is used for converting [.pcx](/Help/Files/PCX.md) files to and from [.bmp](/Help/Files/BMP.md) files.

### PySPK
[PySPK](/Help/Programs/PySPK.md) is used for editing the space paralax [.spk](/Help/Files/SPK.md) files.

### PyTBL
[PyTBL](/Help/Programs/PyTBL.md) is used for editing the strings [.tbl](/Help/Files/TBL.md) files.

### PyTILE
[PyTILE](/Help/Programs/PyTILE.md) is used for editing the [tileset](/Help/Files/Tilesets/Tilesets.md) files ([.cv5](/Help/Files/Tilesets/CV5.md), .vx4, .vf4, .vr4, .dddata)

### PyTRG
[PyTRG](/Help/Programs/PyTRG.md) is used for editing triggers ([.trg](/Help/Files/TRG.md) files)
