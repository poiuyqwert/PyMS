# Building
This page describes what [PyMOD](/Help/Programs/PyMOD.md) actually does when you press **Compile**. You don't need any of it to build a mod, but it explains the messages in the compile log, why sources are built in the order they are, and what the files in `.build` are for.

## Where Files Go
A compile moves your work through three places inside the project's `.build` folder:

1. `.build/intermediates/` holds every compiled game file, in a copy of your project's folder layout. This is the build's working area, and it persists between compiles — it is what makes incremental builds possible.
2. `.build/staging/` is where the finished output is assembled. It is emptied at the start of every compile, so it never contains anything from an earlier build.
3. `.build/artifacts/` is the finished output of your last successful compile, and the only folder you normally care about. It holds the packaged `.mpq` archives, plus every compiled or copied file that is not inside an MPQ folder.

## Compile Order
Steps run in five ordered groups. Everything in one group finishes before the next begins, which is how a step can rely on the output of an earlier one:

1. **Setup**: Creates `.build`, clears out any staging folder left behind by a compile that crashed or was cancelled, loads `.build/meta.json`, and walks your project to work out the list of steps to run. Nearly every step in the groups below is decided here, from the folder layout of your project.
2. **Make intermediates**: Creates the intermediates folders and compiles the sources that need nothing but their own inputs — DAT, GRP, TBL, LO, PCX, and SPK sources, plus copying plain files.
3. **Use intermediates**: Compiles the sources that read other compiled files. [AI scripts](/Help/Programs/PyMOD/AI_Script_Sources.md) and [iscripts](/Help/Programs/PyMOD/IScript_Sources.md) are here, because they resolve names against your project's own compiled TBL and DAT files, which only exist once the previous group has finished.
4. **Make artifacts**: Deletes intermediates that this build no longer produces, packages the [MPQ archives](/Help/Programs/PyMOD/MPQ_Packages.md), and copies the files that are not inside an MPQ into staging. A nested MPQ is always packaged before the archive that embeds it.
5. **Shutdown**: Publishes the staged artifacts and saves `.build/meta.json`.

The first error stops the build; the groups after it don't run. **Cancel** is checked between steps, so a cancelled compile stops at the next step boundary rather than mid-file.

## Incremental Builds
`.build/meta.json` records, for every target the build produces, a hash of each of its outputs and a single fingerprint of the whole set of inputs it was built from. Before compiling anything, a step compares the current state against that record and skips the work when nothing relevant has changed, logging `No changes required` instead.
A rebuild is triggered when any of these is true:

- The target has no record from a previous build.
- An output file is missing, or its contents no longer match what was recorded — so deleting something out of `.build/intermediates` reliably rebuilds it.
- The set of inputs changed, or any input's contents changed.

The input fingerprint covers input **names** as well as contents. This matters more than it sounds: a [GRP source](/Help/Programs/PyMOD/GRP_Sources.md) takes its frame order from its filenames, so renaming `frame 007.bmp` to `frame 070.bmp` changes the compiled GRP even though no pixel changed. Adding and removing inputs is caught the same way.
If a compile fails or is cancelled, the bookkeeping from the steps that already finished is still saved, so the next compile picks up where it left off instead of starting over. In that case the records are kept as-is rather than tidied up, since the steps that never ran didn't get a chance to say which files they still use.

## Publishing Artifacts
Artifacts are only swapped into place once the entire build has succeeded, so a failed or cancelled compile never leaves you without a working build. Publishing moves the previous artifacts aside to `.build/artifacts.old`, moves staging into place as the new `.build/artifacts`, and then removes the old copy.
The previous artifacts are moved aside rather than deleted so they can be put back if the swap itself fails — the one moment in the build where you could otherwise be left with nothing. If clearing `.build/artifacts.old` afterwards fails, the build still succeeds and logs a warning; the folder is cleared by the next compile.

## Cleaning Up
A normal compile already deletes intermediates it no longer produces, so renaming or removing a source doesn't leave its old output behind to be packaged into your mod.
**Clean** deletes the whole `.build/intermediates` folder, forcing the next compile to rebuild every source from scratch. `.build/artifacts` and `.build/meta.json` are left alone, so your last build's output stays where it is. Since the incremental check notices missing output files, a clean build is a matter of deleting the intermediates and compiling again.

## Reading the Log
The compile log opens with the start time and ends with either a green completion message and total duration, or a red error. Warnings are orange, and are worth reading even on a build that succeeds — a source that produced nothing, a `config.json` that couldn't be read, an expanded file that will need a plugin, and a script ID that got overwritten are all warnings rather than errors.
Some errors are followed by an `INTERNAL ERROR` block with a stack trace. That is the underlying failure behind the message, and it is the useful part to include if you report a problem.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [AI Script Sources](/Help/Programs/PyMOD/AI_Script_Sources.md)
- [IScript Sources](/Help/Programs/PyMOD/IScript_Sources.md)
- [Other Sources](/Help/Programs/PyMOD/Other_Sources.md)
- [Building a Mod Project](/Help/Tutorials/Building_a_Mod_Project.md)
