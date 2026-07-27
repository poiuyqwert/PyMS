# SPK Sources
A folder whose name ends with `.spk` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into a [.spk](/Help/Files/SPK.md) parallax star background of the same name. The folder contains a single `.bmp` file with the same base name as the folder, so a `star.spk/` folder is compiled from `star.spk/star.bmp`.
The game's parallax is `parallax\star.spk`, and it is only used on the Space Platform [tileset](/Help/Files/Tilesets/Tilesets.md).

## Layers
A parallax is made of up to 5 [layers](/Help/Programs/PySPK/Layers.md) that each scroll at their own speed. In the BMP the layers are stacked: the image is divided from top to bottom into equal height bands, one per layer, with the top band being layer 1 (the slowest scrolling, deepest layer).

- `layer_count` (default `5`): How many layers the image is divided into, from 1 to 5. A value outside that range fails the build.

The image height has to divide evenly by `layer_count`, and the build fails if it doesn't. Each layer is a 648x488 field that repeats across the map, so that is the size a band should be.

## Stars
Stars are found in the image rather than listed anywhere: any connected group of non-transparent pixels is one star, and palette index 0 is the transparent color. A star is cropped to its own bounding box, and stars whose images come out identical share a single stored image, which is what keeps the file small when a starfield repeats the same few dots.
A star belongs to the layer whose band its top row falls in, so keep stars inside a single band rather than straddling a boundary.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [PySPK](/Help/Programs/PySPK.md)
- [Layers](/Help/Programs/PySPK/Layers.md)
- [SPK](/Help/Files/SPK.md)
- [Editing a Parallax](/Help/Tutorials/Editing_a_Parallax.md)
