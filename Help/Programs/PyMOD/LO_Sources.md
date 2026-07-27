# LO Sources
A folder whose name ends with one of the overlay extensions is compiled by [PyMOD](/Help/Programs/PyMOD.md) into a [.lo?](/Help/Files/LO.md) overlay file of the same name. All ten are supported: `.loa`, `.lob`, `.lod`, `.lof`, `.log`, `.lol`, `.loo`, `.los`, `.lou`, and `.lox`.
The folder contains a single `.txt` file with the same base name as the folder, in the format [PyLO](/Help/Programs/PyLO.md) exports — so a `marine.loa/` folder is compiled from `marine.loa/marine.txt`. There are no settings for LO sources.
An overlay file holds one set of `(x, y)` offsets for every frame of the [GRP](/Help/Files/GRP.md) it attaches to, which is what puts an attack overlay, a shield, or a spawning projectile in the right spot on each frame. Because the offsets are matched to the frames of one specific graphic, an overlay usually needs updating whenever you change the frames of the GRP it goes with.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [GRP Sources](/Help/Programs/PyMOD/GRP_Sources.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [PyLO](/Help/Programs/PyLO.md)
- [LO](/Help/Files/LO.md)
