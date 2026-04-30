# `include`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-include"></a>

## `include`

- Kind: `command`
- Detail: Other - Other

Syntax: `(include <String>)`

DE only. Loads an XS file. For more info on XS scripting, see this exhaustive guide: link. Unlike the load command, the filetype (.xs) must be included in the include command. The filepath must be inside quotes. By default, .xs files must be placed in the game's xs folder, located at: "C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\xs", but you can also load .xs files with a relative filepath name, using "../" to go up a filepath level from the xs folder and then follow the rest of the filepath to get to your .xs file. For example, to include a .xs file stored in your "My AI" folder within the default AI installation directory, you can use (include "../ai/My AI/Example XS File.xs"). Once you have included your .xs file, you can use xs-script-call to call any function from that file that doesn't have any parameters. See the xs-script-call page for more details. Unfortunately, as of this writing, including XS scripts seems to be bugged because it seems to still use the xs folder within the installation directory as the default folder, rather than the xs folder inside the mods folder, making it impossible to specify the correct directory. Additionally, if there are any load or load-random commands that appear later in your AI script, any include commands will not work. In summary, place all load and load-random commands at the top of your AI, and then add your include commands. The include command can be inserted anywhere between rules. Include commands cannot be included inside a rule. Once an .xs file is included, all .xs code that isn't within a function will start running immediately, and any rules within the .xs file will start running periodically if enabled. To call functions from the AI script, use xs-script-call.

[AIRef](https://airef.github.io/commands/commands-details.html#include)

Completion insert text:

```text
(include ${1:String})
```

