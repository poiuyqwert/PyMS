# Converting an Image to PCX
This tutorial walks through converting an image to a [.pcx](/Help/Files/PCX.md) file with [PyPCX](/Help/Programs/PyPCX.md) — for example to replace one of the games menu backgrounds or other UI art.

## Preparing the Image
PyPCX imports images from 256 color [.bmp](/Help/Files/BMP.md) files, so the image first needs to be converted in an image editor:

1. Open your image in any image editor that supports indexed color (like GIMP, Paint Shop Pro, or Photoshop).
2. Convert the image to 256 color (8 bit indexed) mode. If the graphic needs to use a specific StarCraft [palette](/Help/Files/Palettes.md) in the game, convert it using that palette so the pixels map to the right colors.
3. Save the image as a `.bmp` file, with compression turned off (or set to RLE).

## Importing into PyPCX
1. Open PyPCX and press **Import BMP** (`Ctrl+I`), then select your `.bmp` file.
2. The image appears in the preview. If no file was open, PyPCX creates a new untitled PCX for it.

## Applying a Palette
If the image already uses the right colors you can skip this step. To swap in a different palette:

1. Press **Import a palette** (`Ctrl+Alt+I`) and select a palette file — for example one of the StarCraft palettes bundled with PyMS in its `Palettes` folder, or any `.pal`, `.wpe`, `.act`, `.pcx`, or `.bmp` file.
2. The preview recolors to show the new palette.

Note that importing a palette only replaces the colors — the pixels keep their palette positions, they are not remapped to the nearest new color. If the image was converted with a different palette it will look scrambled, and it is better to go back and convert the image with the target palette in your image editor.

## Saving the PCX
1. Press **Save** (`Ctrl+S`) and choose where to save the `.pcx` file.
2. To use it in the game, add it to your mods MPQ at the path of the file you are replacing, using [PyMPQ](/Help/Programs/PyMPQ.md) — see the [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md) tutorial.

## See Also
- [PyPCX](/Help/Programs/PyPCX.md)
- [PCX](/Help/Files/PCX.md)
- [BMP](/Help/Files/BMP.md)
- [Palettes](/Help/Files/Palettes.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
