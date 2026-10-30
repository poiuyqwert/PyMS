# FNT
`.fnt` files contain the bitmap fonts used to draw most of the games UI text.
A font covers a range of ASCII characters (up to the 256 ASCII codes), and stores each letter as a small image up to the fonts max width and height. Letter pixels are not full colors — each pixel is one of up to 8 indexes into a color ramp, which the game maps to actual colors (through the `tfontgam.pcx` special palette) based on the color codes in the text being drawn.

Edited by [PyFNT](/Help/Programs/PyFNT.md) — see the [Editing a Font](/Help/Tutorials/Editing_a_Font.md) tutorial.
