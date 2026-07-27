# PCX Sources
A folder whose name ends with `.pcx` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into a [.pcx](/Help/Files/PCX.md) image of the same name. The folder contains a single `.bmp` file with the same base name as the folder, so a `tfontgam.pcx/` folder is compiled from `tfontgam.pcx/tfontgam.bmp`.
The BMP must be an 8-bit paletted image. Both its pixels and its palette go into the PCX, since a PCX stores its palette inside the file — so the colors you see in the BMP are the colors the game gets. There are no settings for PCX sources.
The game uses PCX images for menu backgrounds and other UI art, and also as small lookup images that act as palettes, like `tfontgam.pcx` for [font](/Help/Files/FNT.md) colors. Either kind works the same way here: edit the BMP, and the compile converts it.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [PyPCX](/Help/Programs/PyPCX.md)
- [PCX](/Help/Files/PCX.md)
- [Converting an Image to PCX](/Help/Tutorials/Converting_an_Image_to_PCX.md)
