# `load-random`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-load-random"></a>

## `load-random`

- Kind: `command`
- Detail: Other - Other

Syntax: `(load-random <Value> <String>)`

Randomly loads the code from one AI file out of a list of files. This command provides an option of randomizing AI strategies on the level higher than the rule level. Notice that the filenames do not have path or an extension. The script interpreter automatically adds a path and an extension. By default, the load-random command will look for a file with a matching filename within the main AI directory. If you want to load a .per file from a folder within the AI directory, enter the name of the folder, followed by a slash, and then followed by the filename without a file extension. Here are the default AI directories per game version:CD Version/UP: C:\Program Files (x86)\Microsoft Games\Age of Empires II\AIWK: C:\Program Files (x86)\Microsoft Games\Age of Empires II\Games\WololoKingdoms\Script.AiDE: C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\aiDE Mods: C:\Users\%USERNAME%\Games\Age of Empires 2 DE\[Your Unique Game ID]\mods\local\[The Mod's Name]\resources\_common\ai (if you want to edit a mod you downloaded, use the subscribed folder instead of the local folder) Using the load-random command makes it easier to organize and re-use parts of your scripts in new ways and to provide variation between games. Loaded files are in every aspect the same as original script files, so any script file can be loaded by any other script file. The load-random command can be inserted anywhere between rules. load-random commands cannot be used inside a rule, so if you want to load your AI code according to a certain condition, use #load-if-defined or #load-if-not-defined. Each file within the load-random is given a percent chance from 1 to 100 for that file to be selected. If a percentage is not provided, this file is regarded as the default file which will be picked if the other files with percentages are not chosen. Only one of the possible files within the load-random command will be selected. If the percentages don't add up to 100 and there is no default file given, then there is a chance that the load-random command will not load any files. If only the default file is given, that file will load 100% of the time, but this version of the load-random command is slower than the load command, so specifying only a default file is not recommended. Userpatch added some additional options for load-random. Instead of a literal numeric percent, you can use a + followed by a defconst which specifies the percent, without spaces. This allows the scripter to randomly load files according to defconsts. You can also use a + to load files with 100% probability. In either case, the + is ignored by the CD version (version AoC) AI parser, so load-random commands using a + will ensure that thes files are only loaded if the player is using Userpatch. As of this writing, the options in this paragraph are bugged in DE. The AI Expert system that AoE2 uses loads all AI files at runtime, so you cannot tell the AI to load a file after a game has started. Once a load-random command has determined which file to randomly load, this selected file will be used throughout the rest of the game. When a load-random command is encountered, parsing of the current file is suspended until the load-random command finishes. At that point parsing resumes, starting with a rule immediately following the load-random command. Essentially, you can think of the load-random command as copying the code from the external .per file and pasting it into the original .per file that has the load-random command. Or, more accurately, if you have programming experience, you can think of the load-random command as a function call. Load commands can be nested (a script that loads another script) up to 10 levels deep. Loading multiple script files from a top-level script file makes computer players' knowledge modular. This approach has a benefit only if the script files loaded do not have overlapping areas of expertise.

[AIRef](https://airef.github.io/commands/commands-details.html#load-random)

Completion insert text:

```text
(load-random ${1:Value} ${2:String})
```

