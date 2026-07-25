# Widget Editor
The Widget Editor edits all the properties of a single widget. Open it with **Edit Widget** on the widgets toolbar, by pressing `Enter`, or by double clicking a widget in the tree or on the canvas.
**Ok** applies the changes and closes the editor, and **Update Preview** applies them while leaving the editor open, so you can tweak values and see the result on the canvas. Closing the editor any other way discards all the changes (including ones already previewed).
The **Advanced** checkbox shows every property of the widget. With it off, properties that don't normally apply to the widgets type are hidden (for example text styling for an Image, or button flags for a Label) — the sections below describe everything, so some fields will only be visible with Advanced on. The Advanced state is remembered between sessions.

## Bounds
The widgets position and size: Left, Top, Right, Bottom, Width, and Height. In simple mode you enter Left, Top, Width, and Height, and the rest is calculated; with Advanced on all six values are editable, and each field has a calculate button to recompute it from the others.

## Mouse Response
The **Responds to Mouse** checkbox sets whether the widget reacts to the mouse at all. The Left/Top/Right/Bottom/Width/Height fields define the responsive hit-box — the area that actually responds to the mouse — relative to the widgets top left corner, which lets the clickable area differ from the visual bounds.

## Text and Images
The string properties. For most widgets the **Text** field is the text displayed on the widget, in the same format as [TBL](/Help/Files/TBL.md) strings — including formatting codes like `<3>` to change the text color. For an Image widget the field is instead the file path of its [PCX](/Help/Files/PCX.md) image inside your MPQs — the browse button next to the field browses your MPQs for one — and **Image Transparency** makes the images background color transparent.

- **Offset**: X/Y offset of the text within the widget.
- **Hotkey**: With **Normal** and/or **Virtual** on, the first character of the text is the widgets hotkey (and is not displayed).
- **Horizontal** and **Vertical**: Text alignment within the widget — Center/Right/Center 2 horizontally, and Top/Middle/Bottom vertically.
- **Font**: The font size used to draw the text — Size 10, 14, 16, or 16x. The canvas renders text with the matching font file from your [Program Settings](/Help/Programs/PyBIN.md#program-settings).

## SMK Animations
SMK settings connect a widget to an [SMK](/Help/Files/SMK.md) video, used for the animated art on the games menus (normally on Highlight Buttons). The dropdown attaches one of the files existing SMK animations to the widget (or `None`), the edit button opens the attached animation in the SMK editor, and the add button creates a new animation and attaches it. **Translucent** renders the SMK with translucency.
The SMK editor edits the animation itself:

- **Filename**: The path of the `.smk` video inside your MPQs. The find button browses your MPQs for one.
- **Overlay SMK**: Another SMK animation to draw on top of this one, with an **Offset X**/**Offset Y** position. Overlays can chain, but can't form a loop.
- **Flags**: **Fade In**, **Dark**, **Repeat Forever**, and **Show on Hover** (only draw the animation while the mouse is over the widget), plus four unknown flags.

Like the Widget Editor, the SMK editor has **Ok** and **Update Preview** buttons, and closing it any other way discards the changes. Note that SMK animations are stored in the file separately from widgets — editing an animation affects every widget it is attached to.

## Other Properties
- **State**: **Visible** (widgets with this off are only drawn on the canvas when the **Hidden** preview setting is on) and **Disabled**.
- **Sounds**: **No Hover** and **No Click** suppress the games hover/click sounds on interactive widgets.
- **Btn. Type**: **Default** (the button activated by `Enter` in the game) and **Cancel** (activated by `Esc`).
- **SC:R**: An unknown value that only exists in Remastered files (only editable when the file is in SC:R mode).
- **Misc.**: **Bring to Front** draws the widget on top, **Control ID** is the widgets numeric identifier (used by the game to find the widget, so be careful changing it on existing widgets), and the numbered **Unknown** checkboxes are flags with unidentified purposes.

## See Also
- [PyBIN](/Help/Programs/PyBIN.md)
- [Widgets](/Help/Programs/PyBIN/Widgets.md)
- [UI BIN](/Help/Files/UI_BIN.md)
