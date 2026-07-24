# Layers
A parallax is made up of up to 5 layers of stars. Each layer is a 648x488 tile that repeats to cover the whole map, and scrolls at its own speed as the screen moves: Layer 1 scrolls the slowest (appearing deepest in the background), and each layer after it scrolls a little faster (appearing closer).
The Layers panel in [PySPK](/Help/Programs/PySPK.md) lists the layers in the open parallax. Each row has:

- An eye button that toggles the layers visibility in the editor. Stars on hidden layers are not shown on the canvas and can not be selected.
- A lock button that locks the layer. Stars on locked layers can not be selected or drawn over.
- The layer name — click it (or anywhere on the row) to make it the active layer, which is the layer the **Draw** tool places stars on. The active layer is highlighted.

Visibility and locking only affect editing in PySPK — they are not saved into the `.spk` file.
The toolbar below the list manages the layers:

- **Add Layer** (`Insert`): Adds a new empty layer (up to the maximum of 5) and makes it the active layer.
- **Remove Layer** (`Delete`): Deletes the active layer, asking for confirmation if it has any stars.
- **Move Layer Up** and **Move Layer Down**: Moves the active layer up or down the list, changing its scroll speed.
- **Auto-lock**: While on (the default), selecting a layer automatically locks all the other layers, so you only ever edit one layer at a time.
- **Auto-visibility**: While on, selecting a layer automatically hides all the other layers, showing just the layer you are working on.

## See Also
- [PySPK](/Help/Programs/PySPK.md)
- [Palette Tab](/Help/Programs/PySPK/Palette_Tab.md)
- [Stars Tab](/Help/Programs/PySPK/Stars_Tab.md)
- [SPK](/Help/Files/SPK.md)
