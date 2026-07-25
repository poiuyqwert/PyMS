# iscript.bin
`iscript.bin` contains the animation scripts (IScripts) that control the games graphics. Each [images.dat](/Help/Files/DAT/images.dat.md) entry references an IScript entry by its ID, and the script controls everything the image does: which [GRP](/Help/Files/GRP.md) frames are displayed, spawning overlays and sprites, playing sounds, movement and turning, and the timing of attacks and spells.
Each IScript entry has a header, which declares the entry's ID and type, and lists the entry points for its [animations](#animations) — the type determines which animations the entry has. The game plays an animation by running the script from that animation's entry point.
`iscript.bin` has a maximum file size of 65535 bytes.

Edited by [PyICE](/Help/Programs/PyICE.md). The text language it is decompiled to and compiled from is documented in [IScript Language](/Help/Programs/PyICE/IScript_Language.md).

## Animations
There are 28 animations. Which of them an entry has is determined by the entry's type (see [Script Headers](/Help/Programs/PyICE/IScript_Language.md#script-headers)); an entry can also leave an animation it has empty (except `Init`).

1. **Init**: Initial animation.
2. **Death**: Death animation.
3. **GndAttkInit**: Initial ground attack animation.
4. **AirAttkInit**: Initial air attack animation.
5. **Unused1**: Unknown/unused animation.
6. **GndAttkRpt**: Repeated ground attack animation.
7. **AirAttkRpt**: Repeated air attack animation.
8. **CastSpell**: Spell casting animation.
9. **GndAttkToIdle**: Animation for returning to an idle state after a ground attack.
10. **AirAttkToIdle**: Animation for returning to an idle state after an air attack.
11. **Unused2**: Unknown/unused animation.
12. **Walking**: Walking/moving animation.
13. **WalkingToIdle**: Animation for returning to an idle state after walking/moving.
14. **SpecialState1**: Some sort of category of special animations, in some cases an in-transit animation, sometimes used for special orders, sometimes having to do with the animation when something finishes morphing, or the first stage of a construction animation.
15. **SpecialState2**: Some sort of category of special animations, in some cases a burrowed animation, sometimes used for special orders, sometimes having to do with the animation when canceling a morph, or the second stage of a construction animation.
16. **AlmostBuilt**: An animation for one part of the building process.
17. **Built**: Final animation before finishing being built.
18. **Landing**: Landing animation.
19. **LiftOff**: Lifting off animation.
20. **IsWorking**: Animation for when researching an upgrade/technology or training/building units and some other animations for some sort of work being done.
21. **WorkingToIdle**: Animation for returning to an idle state after IsWorking.
22. **WarpIn**: Warping in animation.
23. **Unused3**: Unknown/unused animation.
24. **StarEditInit**: Previously called InitTurret, this is actually an alternate initial animation for StarEdit a.k.a. the Campaign Editor.
25. **Disable**: Animation for becoming disabled, either through the "Set Doodad State" trigger action or by not being in the psi field of any pylons.
26. **Burrow**: Burrowing animation.
27. **UnBurrow**: Unburrowing animation.
28. **Enable**: Animation for becoming enabled, either through the "Set Doodad State" trigger action or by being in the psi field of a pylon.

## See Also
- [PyICE](/Help/Programs/PyICE.md)
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [images.dat](/Help/Files/DAT/images.dat.md)
- [GRP](/Help/Files/GRP.md)
