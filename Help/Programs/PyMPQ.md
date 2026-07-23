# PyMPQ
PyMPQ is a tool used for editing [.mpq](/Help/Files/MPQ.md) files, which are the containers for all the data files in the game. PyMPQ allows you to view all the files in an `.mpq`, extract files from them, and add new files to them with your choice of [compression, encryption](#compression-and-encryption), and [locale](#locales). If you are packaging a mod, start with the [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md) tutorial.
MPQ support requires the StormLib or SFmpq library, which PyMS currently only includes for Windows and Mac. The status bar shows which library is in use.

## Main Window
The window shows the list of files in the open archive, with a column for each piece of information:

- **Name**: The full path of the file inside the archive. MPQ paths use `\` separators, for example `music\title.wav`.
- **Size**: The original (uncompressed) size of the file.
- **Ratio**: How much of the original size the file takes up as stored in the archive.
- **Packed**: The size of the file as stored in the archive.
- **Locale**: The numeric [locale](#locales) of the file.
- **Attributes**: `C` if the file is compressed, `E` if it is encrypted, and `X` if its encryption key is adjusted (each shows as `-` when not set).

Click a column header to sort the list by that column, and click it again to reverse the order. Multiple files can be selected at once (`Shift` and `Ctrl` clicking), and the status bar shows the count and total size of the selected files.
The **Filter** box above the list narrows the list down to the matching file names, and keeps a history of your filters. Press `Enter` or the find button to apply the filter. In **Wildcard** mode `*` matches anything and `?` matches any single character (for example `unit\*.grp`), while **Regex** mode matches full regular expressions (the box flashes red if the pattern is not valid).
The status bar also shows the file counts and total size of the archive, the [locale](#locales) used for newly added files, and the MPQ library in use.

## Managing Archives
- **New** (`Ctrl+N`): Creates a new empty archive. The file capacity and block size of new archives are configured in the [settings](#settings).
- **Open** (`Ctrl+O`): Opens an existing archive. Other non-PyMS programs may lock an MPQ while they have it open, so if an archive fails to open, try closing any program that might be using it.
- **Close** (`Ctrl+W`): Closes the archive.
- **Compact Archive** (`Ctrl+P`): Rebuilds the archive to reclaim the space left behind by deleted and replaced files. It is only enabled when there is space to reclaim — the file counts in the status bar show the listed files against the space used in the archive.
- **Set as default `*.mpq` editor** (Windows only): Associates `.mpq` files with PyMPQ, so they open in PyMPQ when double clicked.

## Managing Files
- **Add Files** (`Ctrl+I`): Adds the chosen files to the archive. A folder prompt lets you type a path to put at the start of every added file name — for example typing `music\` adds `title.wav` as `music\title.wav`. The prefix is remembered for next time.
- **Add Directory** (`Ctrl+D`): Adds every file inside the chosen folder (including subfolders, which become part of the file paths), with the same folder prompt for an extra prefix.
- **Extract Files** (`Ctrl+E`): Extracts the selected files to a chosen folder, recreating the folder structure of their paths.
- **Delete Files** (`Delete`): Removes the selected files from the archive.
- **Rename File** (`Ctrl+R`): Renames the selected file by editing its name directly in the list.

Right clicking the list opens a menu with **Open** (see [Opening and Editing Files](#opening-and-editing-files)), **Extract**, **Delete**, **Rename**, and **Change Locale** (see [Locales](#locales)).
Files are added using the current [compression, encryption](#compression-and-encryption), and [locale](#locales) settings.

## Opening and Editing Files
Double click a file (or right click and choose **Open**) to open it with the default program for its file type. The file is extracted to a temporary folder, and PyMPQ watches it while you edit: whenever the file is saved, PyMPQ offers to update the archive with the changes (if several open files were modified, a dialog lets you pick which ones to update). This makes it easy to edit files without manually extracting and re-adding them.
The temporary files are cleaned up when the archive is closed or PyMPQ exits.

## Compression and Encryption
The **Manage Settings** toolbar button opens a menu controlling how files are stored when they are added. These settings apply to files added afterwards — they do not change files already in the archive. The compression choices are:

- **Auto-Select** (`F4`): Picks the compression for each file based on its extension, using the table from the [Compression Auto-Selection](#settings) settings. With the default table, `.wav` files use Audio compression, `.smk` and `.mpq` files are stored uncompressed, and everything else uses Standard.
- **None** (`F2`): Stores files uncompressed. Best for files that are already compressed, which can grow when compressed again.
- **Standard** (`F3`): PKWare compression, the standard used by the games own archives.
- **Deflate**: Zlib compression, usually smaller than Standard. The submenu picks the compression level, from `0 (None)` to `9 (Best Compression)`, or the zlib default level (`F9`).
- **Audio**: Lossy audio compression for `.wav` sound files, at three quality levels: **Lowest (Best Quality)** (`F6`), **Medium** (`F7`), and **Highest (Least Space)** (`F8`). Since it is lossy, keep backups of your original sounds.

The menu also has **Encrypt** (`F5`), which encrypts files as they are added, and the [Locale](#locales) for added files.

## Locales
Every file in an MPQ has a locale, identifying which language version of the game it is for. The game loads the file matching its language, falling back to the file with the Neutral locale `[0]`. Most files (and most mods) just use Neutral.
The **Locale** submenu of the **Manage Settings** menu sets the locale given to newly added files — either one of the named game languages, or **Other** to type a custom locale number (0 to 65535). The current choice is shown in the status bar.
To change the locale of files already in the archive, select them and choose **Change Locale** from the right click menu.

## Settings
**Settings Dialog** (`Ctrl+M`, also at the top of the **Manage Settings** menu) configures PyMPQ:

- **General**: **Max Files** is the file capacity of newly created archives (it cannot be changed for an existing archive), and **Block Size** is the block size of newly created archives.
- **List Files**: MPQ archives do not reliably store the names of their files, so PyMPQ uses list files to identify the files in an archive by name. A standard list file for the games files is included by default, and you can add your own. Note: each list file added will increase the load time for archives.
- **Compression Auto-Selection**: Edits the table used by the **Auto-Select** [compression](#compression-and-encryption) setting. Add or remove file extensions and choose the compression type (and level) for each; the **Default** entry is used for any extension not in the table.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## See Also
- [MPQ](/Help/Files/MPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
- [Themes](/Help/Programs/Themes.md)
