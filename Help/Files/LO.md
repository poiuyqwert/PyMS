# LO?
`.lo?` files contain offset data, which the game uses to position things relative to a unit's [GRP](/Help/Files/GRP.md) graphics — like where overlay graphics are drawn, or where projectiles spawn. A `.lo?` file contains one set of offsets for each frame of the graphic it attaches to, and each frame contains one `(x, y)` pixel offset per overlay. Every frame has the same amount of overlays, and each coordinate ranges from -128 to 127.
There are various different file extensions for different purposes:
- `.loa`: Attack Overlays
- `.lob`: Zerg Birth Overlays
- `.lod`: Landing Dust Overlays
- `.lou`: Liftoff Dust Overlays
- `.lof`: Building Fire Overlays
- `.loo`: Powerup Pickup Offsets
- `.los`: Shield/Smoke Overlays
- `.log`: Misc.
- `.lol`: Misc.
- `.lox`: Misc.

Edited by [PyLO](/Help/Programs/PyLO.md), which decompiles the offsets into an easy to edit text format (see [LO Source Syntax](/Help/Programs/PyLO/Code_Editor.md#lo-source-syntax)).
