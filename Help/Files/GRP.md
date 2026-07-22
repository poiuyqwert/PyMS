# GRP
`.grp` files contain the graphics for most of the in game elements, like [Units](/Help/Files/DAT/units.dat.md), [Doodad Sprites](/Help/Files/Tilesets/CV5.md#doodads), [Icons](/Help/Files/GRP.md#cmdicongrp), etc. This does not include terrain, most UI and menu elements.

Edited by [PyGRP](/Help/Programs/PyGRP.md)

## Format
A GRP contains a sequence of frames (up to 2400), all sharing the same canvas size of up to 256x256 pixels. Each frame also stores the bounds of its visible pixels within that canvas, so the transparent space around a frame takes no room in the file.
The graphics are in 8-bit indexed color: each pixel is an index into a 256 color [palette](/Help/Files/Palettes.md). The palette itself is not stored in the GRP — the game applies the appropriate palette when drawing (PyMS comes with matching palettes, like `Units.pal` for unit graphics). One palette index (normally index 0) is treated as transparent, and on unit graphics indexes 8 to 15 are drawn as the player's color.

## Compression
Frame pixels are normally compressed line by line with a simple run-length encoding (runs of transparent pixels, runs of a single repeated color, and runs of literal pixels), and identical frames or lines can be stored once and shared. Some GRPs are instead stored uncompressed, as raw pixels. Nothing in the file marks which form is used, so tools have to detect or be told — when [PyGRP](/Help/Programs/PyGRP.md) opens an uncompressed GRP it shows a notice reminding you to check **Save Uncompressed**, so the file is saved back in the same form.

## Framesets
Graphics that rotate, like most units, store 17 frames for each animation step — one per facing direction, covering the half circle from facing up to facing down (the game mirrors them horizontally to draw the other half). Each group of 17 frames is called a frameset, so for example frame 0 and frame 17 are the same facing direction in two consecutive animation steps. PyGRP indents alternating framesets in its frames list, and can step or play its preview 17 frames at a time, to make working with framesets easier.

## cmdicon.grp
`cmdicon.grp` contains the icons for [Weapons](/Help/Files/DAT/weapons.dat.md), [Upgrades](/Help/Files/DAT/upgrades.dat.md), [Orders](/Help/Files/DAT/orders.dat.md), etc.
