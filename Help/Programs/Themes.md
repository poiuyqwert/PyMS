# Themes
PyMS supports themes to adjust the look of the programs. This documentation provides some help on how to customize/build your own themes. PyMS comes with one theme built in, the "Dark" theme. You can take a look at its contents for an example.


Themes are located in the `PyMS/PyMS/Themes` folder as `.txt` files. They contain JSON, with a specific structure and set of keys. At the root of the theme, you should provide these main keys:
- `"author"`: The author of the theme
- `"description"`: The description of your theme
- `"widgets"`: Where you will build the styles to apply to the [Widgets](#widgets) in the programs, using [Selectors](#selectors), [Settings](#settings), and [Values](#values)
- `"colors"`: [Additional Colors](#additional-colors) for internal parts of widgets (like some text styling in the Help dialog)


If you are having trouble with a theme, you can check the log file of the program you are running (located in `PyMS/PyMS/Logs`) for errors that are reported about the active theme.


## Selectors
Selectors are rules on how to select specific widgets to apply style settings to. The most basic selector is the "default" selector using `"*"`, it applies to all widgets regardless. More specific selectors can be built using a combination of "matchers":
- **Program Matcher**: You can specify a program matcher at the beginning of a selector using `[ProgramName]` (for example `[PyDAT]`). This matcher will only match widgets for that program
- **Widget Matcher**: You can specify specific widget types, using `WidgetType` (for example `Label`). An optional "tag" can be added like `WidgetType.TagName` to match only specific cases of the widget type that are tagged for specific uses (for example some `Canvas` widgets are tagged specifically as `preview` widgets). This matcher will only match widgets of the specified type, with the specified tag.
- **Wildcard Matcher**: You can specify a single wildcard `*` or a greedy wildcard `**`, which is useful when matching nested widgets (described later). A single wildcard will match a single widget of any type, a greedy wildcard will match as many widgets of any type it can.


These matchers can be combined into a selector, using spaces between them. When read left to right, they specify a hierarchy to match widgets that are nested in eachother. Some examples of selectors and what they match:
- `"Label"`: Matches any `Label` widget
- `"StatusBar Label"`: Matches any `Label` that is a direct child of a `StatusBar`
- `"Toolbar ** Button"`: Matches any `Button` that is inside a `Toolbar`, no matter how nested it is
- `"[PyDAT] Canvas"`: Matches any `Canvas` in the `PyDAT` program
- `"Canvas.preview"`: Matches any `Canvas` that is tagged as a `preview`


These selectors have a defined collection of settings which will apply only to the widgets that the selector matches. All selectors that match a widget will apply settings to that widget, but they will be applied in the order of which selector is more "specific". The more matchers and specific details there are in the selector, the higher its priority. For example if you have these selectors and settings:


```
"*": {
	"foreground": "#FFFFFF"
	"background": "#111111"
},
"Label": {
	"background": "#222222"
},
"StatusBar Label": {
	"background": "#333333"
}
```


Any `Label` in a `StatusBar` will have the background color `#333333`, and the text color `#FFFFFF`. Any `Label` not inside a `StatusBar` will have the background color `#222222`, and the text color `#FFFFFF`. Every other widget will have the background color `#111111`, and the text color `#FFFFFF`.


## Settings
There is a defined set of settings which can be appled to widgets. Note that not all settings will have an effect on all widget types.
- **foreground**: The text [Color](#values)
- **activeforeground**: The text [Color](#values) when the mouse is over the widget
- **disabledforeground**: The text [Color](#values) when the widget is disabled
- **background**: The background [Color](#values)
- **activebackground**: The background [Color](#values) when the mouse is over the widget
- **disabledbackground**: The background [Color](#values) when the widget is disabled
- **readonlybackground**: The background [Color](#values) when the widget is read only
- **borderwidth**: An [Integer](#values) border width
- **activeborderwidth**: An [Integer](#values) border width to apply when the mouse is over the widget
- **activestyle**: The [Style](#values) to apply to listbox items when they are active (different from selected)
- **highlightcolor**: The [Color](#values) to display in the tab traversal highlight region when the widget has input focus
- **highlightthickness**: An [Integer](#values) for the thickness of the tab traversal highlight rectangle when the widget has input focus
- **highlightbackground**: The [Color](#values) to display in the tab traversal highlight rectangle when the widget does not have the input focus
- **relief**: The [Relief](#values) to apply to a widgets border
- **offrelief**: The [Relief](#values) to apply to a widgets border when in its "off" state
- **overrelief**: The [Relief](#values) to apply to a widgets border when the mouse is over the widget
- **selectforeground**: The text [Color](#values) for selected items
- **selectbackground**: The background [Color](#values) for selected items
- **selectborderwidth**: An [Integer](#values) border width for selected items
- **inactiveselectbackground**: The [Color](#values) of the selection in a `Text`/`Entry` widget when its window is not active
- **insertbackground**: The [Color](#values) for the insertion cursor in a `Text`/`Entry` widget
- **insertborderwidth**: An [Integer](#values) border width for the insertion cursor in a `Text`/`Entry` widget
- **insertofftime**: An [Integer](#values) to specify the amount of milliseconds the insertion cursor is not displayed when blinking
- **insertontime**: An [Integer](#values) to specify the amount of milliseconds the insertion cursor is displayed when blinking
- **insertwidth**: An [Integer](#values) to specify the total width of the insertion cursor (including border if applied)
- **selectcolor**: The background [Color](#values) of a checkbox/radiobox (Note: if the `Checkbutton`/`Radiobutton` is styled as a button, it will be the background of the button)
- **troughcolor**: The [Color](#values) to use for the rectangular trough areas in widgets such as scrollbars and scales (Note: This option is ignored for scrollbars on Windows)


## Values
Each settings value has a specific type (see the [Settings](#settings) for which value type the setting has), and each type has a specific set of rules for how to set them.
- **Color**: A string with a standard hex color code (like whats used in HTML). For example `"#3b4754"`
- **Integer**: A numeric value without decimals. For example `2`
- **Style**: A string witih a style which can be one of these options: `"dotbox"`, `"none"` or `"underline"`
- **Relief**: A string with the border releif which can be one of these options: `"raised"`, `"sunken"`, `"flat"`, `"ridge"`, `"solid"` or `"groove"`


## Widgets
This section lists the widget types that can be used for your [Selectors](#selectors). Some widgets are built as a component comprised of muliple other widgets. Usually these component widgets are based off of a `Frame` with other widgets inside itself. These types of component widgets will match their "super types" as well as their specific types, with their super types being cosidered less specific. So `Frame` would match a `Toolbar`, but if you use `Toolbar` it is more specific and thus has a higher priority than `Frame`.

Widgets:
- `MainWindow`: The main window of the program
- `Toplevel`: Child windows of the program
- `Frame`: A generic container used to group other widgets
- `Button`: A standard button
- `Checkbutton`: A checkbox which could look like a standard checkbox or as a button depending on the situation in the programs
- `Radiobutton`: A radio (like a round chechbox that you can only select one of them) which could look like a standard radio or as a button depending on the situation in the programs
- `Label`: A basic non-selectable/editable text display
- `Entry`: A single line text box where you can type
- `Text`: A multi line text box where you can type
- `Listbox`: A list of items you can select from
- `Scrollbar`: A standard scrollbar
- `LabelFrame`: A frame that has a label to group items under, usually with a border
- `PanedWindow`: A resizable pane, that you can drag to make either side larger or smaller

Components:
- `DropDown`: A standard preset options dropdown. Made from a `Frame`, with an `Entry` and a `Button` as children
- `TextDropDown`: Like a basic `Entry` you can type in but with a dropdown (usually for a history of previous entries). Made from a `Frame`, with an `Entry` and a `Button` as children
- `DropDownChooser`: The list of items presented for a `DropDown`/`TextDropDown`. Made from a `Toplevel`, with a `Listbox` and `Scrollbar` as children
- `Hotlink`: A clickable link. Made from a `Label`
- `Notebook`: A standard notebook, which has pages that can be switched between with tabs. Made from a `Frame`, with `Button` used for the tabs, and other widgets for the pages
- `RichList`: Like a `Listbox` but with more rich options for display of the items. Made from a `Frame`, with `Text` and `Scrollbar` children
- `ReportList`: Like a list with multiple columns. Made from a `Frame`, with `PanedWindow` and `RichList` children
- `ScrolledCanvas`: A convenience to make a scrolled `Canvas`. Made from a `Frame`, with `Canvas` and `Scrollbar` children
- `ScrolledListbox`: A convenience to make a scrolled `Listbox`. Made from a `Frame`, with `Listbox` and `Scrollbar` children
- `ScrollView`: A convenience to allow any widgets to be scrollable if they are too large for their container. Made from a `Frame`, with `Canvas`, `Scrollbar`, and any other widgets for the contents
- `StatusBar`: A statusbar displayed at the bottom of windows. Made from a `Frame`, with `Label` children
- `Toolbar`: A toolbar to display a row of buttons. Made from a `Frame`, with `Button`, `Checkbutton` and `Radiobutton` children grouped in their own `Frame` rows
- `Tooltip`: A tooltip window displayed when you hover over something to get help. Made from a `Toplevel`, with `Frame` and `Label` children
- `TreeList`: A standard tree list. Made from a `Frame`, with `Text` and `Scrollbar` children


## Additional Colors
Some internal parts of widgets can be customized with colors. They are grouped in the `"colors"` section. 

### "help"
The `"help"` group has colors used in the help dialog:
- `"linkforeground"`: The text [Color](#values) to apply to links
- `"codebackground"`: The background [Color](#values) to apply to code spans/blocks
