# `load`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-load"></a>

## `load`

- Kind: `command`
- Detail: Other - Other

Syntax: `(load <String>)`

Loads the code from a separate .per AI file with the given filename. Notice that the filename does not have path or an extension. The script interpreter automatically adds a path and an extension. By default, the load command will look for a file with a matching filename within the main AI directory. If you want to load a .per file from a folder within the AI directory, enter the name of the folder, followed by a slash, and then followed by the filename without a file extension. Here are the default AI directories per game version:CD Version/UP: C:\Program Files (x86)\Microsoft Games\Age of Empires II\AIWK: C:\Program Files (x86)\Microsoft Games\Age of Empires II\Games\WololoKingdoms\Script.AiDE: C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\aiDE Mods: C:\Users\%USERNAME%\Games\Age of Empires 2 DE\[Your Unique Game ID]\mods\local\[The Mod's Name]\resources\_common\ai (if you want to edit a mod you downloaded, use the subscribed folder instead of the local folder) Using the load command makes it easier to organize and re-use parts of your scripts in new ways. Loaded files are in every aspect the same as original script files, so any script file can be loaded by any other script file. The load command can be inserted anywhere between rules. Load commands cannot be used inside a rule, so if you want to load your AI code according to a certain condition, use #load-if-defined or #load-if-not-defined. If you want to randomly select a file to load from a list of files, use load-random. The AI Expert system that AoE2 uses loads all AI files at runtime, so you cannot tell the AI to load a file after a game has started. It is important to mention that the load command executes immediately. This means that when a load command is encountered, parsing of the current file is suspended until the load command finishes. At that point parsing resumes, starting with a rule immediately following the load command. Essentially, you can think of the load command as copying the code from the external .per file and pasting it into the original .per file that has the load command. Or, more accurately, if you have programming experience, you can think of the load command as a function call. Load commands can be nested (a script that loads another script) up to 10 levels deep. Loading multiple script files from a top-level script file makes computer players' knowledge modular. This approach has a benefit only if the script files loaded do not have overlapping areas of expertise.

[AIRef](https://airef.github.io/commands/commands-details.html#load)

Completion insert text:

```text
(load ${1:String})
```

