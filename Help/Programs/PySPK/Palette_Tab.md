# Palette Tab
The Palette tab holds the library of star images in the open parallax — every distinct image stored in the [.spk](/Help/Files/SPK.md) file, displayed in color using the `platform.wpe` palette from your [settings](/Help/Programs/PySPK.md#settings).
Click an image to choose it as the drawing image — the image outlined in white is the one the **Draw** [tool](/Help/Programs/PySPK.md#editing-stars) places on the canvas. The mouse wheel scrolls the list.
Stars placed on the layers share these images, so a parallax can show many stars while only storing a few images. When saving, images with identical pixels are automatically combined into one.
The toolbar at the bottom has the tool buttons, plus:

- **Export Star**: Saves the chosen star image to an 8-bit [.bmp](/Help/Files/BMP.md) file.
- **Import Star**: Loads an 8-bit `.bmp` file as a new star image and adds it to the library. Use the colors of the `platform.wpe` palette, with black (palette index 0) as the transparent background.

## See Also
- [PySPK](/Help/Programs/PySPK.md)
- [Layers](/Help/Programs/PySPK/Layers.md)
- [Stars Tab](/Help/Programs/PySPK/Stars_Tab.md)
- [BMP](/Help/Files/BMP.md)
