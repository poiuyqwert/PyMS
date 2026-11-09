# Syntax Highlighting
The programs with a code editor ([PyAI](/Help/Programs/PyAI/Code_Editor.md), [PyICE](/Help/Programs/PyICE/Code_Editor.md), [PyTRG](/Help/Programs/PyTRG/Code_Editor.md), [PyLO](/Help/Programs/PyLO/Code_Editor.md), and [PyGRAFT](/Help/Programs/PyGRAFT.md#script)) color their code with syntax highlighting. Each program has its own colors, which you customize with its **Color Settings** dialog (`Ctrl+Alt+C`, from the code editor's toolbar, or **Settings > Syntax Highlighting...** in PyTRG and PyLO).

## Color Settings
The list on the left has every style the program uses. Selecting one shows its description and lets you change it:
- **Foreground**: The text color. Uncheck it to use the editor's normal text color, or click the swatch to pick a color.
- **Background**: The background color behind the text. Uncheck it to use the editor's normal background, or click the swatch to pick a color.
- **Bold**: Makes the text bold.

Changes are shown in the editor as soon as you press **Ok**, and **Cancel** undoes all of the changes made in the dialog (including imports and resets).

The toolbar under the list has:
- **Import...**: Loads the colors from a [Syntax Highlighting File](#syntax-highlighting-file). Only the styles this program uses are changed, and any others in the file are ignored.
- **Export...**: Saves this program's colors to a [Syntax Highlighting File](#syntax-highlighting-file). If the file already exists, the styles of the other programs in it are kept, so you can build one file with every program's colors by exporting from each program to the same file.
- **Reset to Defaults**: Opens a menu to change **All Styles** or only the **Selected Style** back to the program's defaults.

## Sharing Colors
Every program uses the same name for the same kind of style, so a `number` style exported from PyAI is the `number` style in PyTRG, PyLO, PyICE, and PyGRAFT too. To make all of the programs match, export from one program and import that file into the others. A syntax highlighting file can also be copied to another computer or shared with other people.

## Syntax Highlighting File
A syntax highlighting file is a `.json` file with a `version` (currently `1`) and a `highlights` object. Each style in `highlights` is keyed by its [style name](#style-names), and has a `foreground` color, a `background` color (`#RRGGBB`, or `null` for none), and whether it is `bold`:

```json
{
    "version": 1,
    "highlights": {
        "comment": {
            "foreground": "#008000",
            "background": null,
            "bold": false
        },
        "number": {
            "foreground": "#FF0000",
            "background": null,
            "bold": false
        }
    }
}
```

A file doesn't need every style. Styles that are left out are not changed when importing.

## Style Names
- `comment`: Comments (all programs)
- `string`: Quoted strings (PyAI, PyGRAFT)
- `tbl_format`: TBL formatted characters, like `<0>` (PyAI, PyTRG)
- `header`: Section headers (PyAI, PyICE, PyTRG, PyLO)
- `ai_id`: AI script IDs (PyAI)
- `block`: Block labels (PyAI, PyICE)
- `command`: Command names (PyAI, PyICE, PyGRAFT)
- `aise_command`: AISE command names (PyAI)
- `header_command`: Header command names (PyICE)
- `type`: Type names (PyAI)
- `directive`: `@directives` (PyAI)
- `keyword`: Keywords (PyAI, PyICE, PyTRG)
- `aise_keyword`: AISE keywords (PyAI)
- `condition`: Condition names (PyTRG)
- `action`: Action names (PyTRG)
- `constant`: Constant references (PyTRG)
- `constant_definition`: Constant definitions (PyTRG)
- `number`: Numbers (all programs)
- `operator`: Operators (all programs)
- `newline`: Newlines (all programs)
- `selection`: Selected text (all programs)
- `error`: Highlighted errors (all programs)
- `warning`: Highlighted warnings (all programs)

## See Also
- [Themes](/Help/Programs/Themes.md)
