# Orders Tab
The Orders tab of [PyDAT](/Help/Programs/PyDAT.md) edits [orders.dat](/Help/Files/DAT/orders.dat.md), which contains the settings for all the orders in the game — the commands units carry out, like Move, Attack Unit, or Gather.

## Order Properties
- **Targeting**: The [Weapon](/Help/Programs/PyDAT/Weapons.md) whose targeting rules the order uses.
- **Energy**: The [Technology](/Help/Programs/PyDAT/Techdata.md) whose energy cost is used when running the order.
- **Obscured**: The order used instead when the target is obscured (under fog of war).
- **Label**: The orders name string in `stat_txt.tbl`.
- **Animation**: The [IScript animation](/Help/Files/iscript.bin.md#animations) played while the order runs.
- **Highlight**: The icon highlighted on the command card while the order runs (or None) — pick it by ID, or click the preview or find button to browse all the icons visually.
- **ReqIndex**: The orders requirements index.

## Flags
The orders behavior flags: Use Weapon Targeting, Changes Subunit Order, Can be Interrupted, Waypoints Slowdown, Can be Queued, Disabled Maintain Unit Target, Obstructable, and Flee Unreturnable Damage. A few flags are unused by the game and labeled as such: Secondary Order, Allow Non-Subunits, Allow Subunits, and Requires Movable Unit. Hover over each flag for an explanation.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the order in their AI Actions.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [orders.dat](/Help/Files/DAT/orders.dat.md)
