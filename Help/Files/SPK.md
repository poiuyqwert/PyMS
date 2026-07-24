# SPK
`.spk` files contain a parallax star background, which is displayed behind the terrain on the Space Platform [tileset](/Help/Files/Tilesets/Tilesets.md). A parallax holds up to 5 layers of stars, and each layer is a 648x488 field that repeats across the map and scrolls at its own speed as the screen moves, creating an illusion of depth.
The star graphics are stored inside the file itself as 8-bit images, colored in the game by the tilesets `platform.wpe` [palette](/Help/Files/Palettes.md). Each placed star references one of the stored images, so many stars can share a single image.
The games parallax is the file `parallax\star.spk` in its [MPQs](/Help/Files/MPQ.md).

Edited by [PySPK](/Help/Programs/PySPK.md)
