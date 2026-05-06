# `xs-script-call`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-xs-script-call"></a>

## `xs-script-call`

- Kind: `command`
- Detail: Fact/Action - Debugging, Goals, Strategic Numbers, Other

Syntax: `(xs-script-call <String>)`

DE only. Call an XS script function from an .xs file. It is not necessary to defconst the function name. If the function name is misspelled or a function with that name doesn't exist in any included .xs files, the command will do nothing, without reporting an error. For more info on XS scripting, see this exhaustive guide: link. The function must be from a .xs file that has been "included" (loaded) by the AI script. To include a .xs file in an AI script, use the include command, like (include "Example XS File.xs"). Note that the filetype (.xs) must be included in the include command, and the filepath must be inside quotes. By default, .xs files must be placed in the game's xs folder, located at: "C:\Program Files (x86)\Steam\steamapps\common\AoE2DE\resources\_common\xs", but you can also load .xs files with a relative filepath name, using "../" to go up a filepath level from the xs folder and then follow the rest of the filepath to get to your .xs file. For example, to include a .xs file stored in your "My AI" folder within the default AI installation directory, you can use (include "../ai/My AI/Example XS File.xs"). Once you have included your .xs file, you can use xs-script-call to call any function from that file that doesn't have any parameters. So, if you have the code below in your XS file, you can call the helloWorld() function, but not the max() function. xs-script-call can be used as either a Fact or an Action, and it'll execute the function either way. However, if used as a Fact, xs-script-call will be a Fact that is considered false if your function returns 0, returns "false", or is a void function that doesn't return anything. Because of this, if you want to use xs-script-call successfully anywhere in a rule, it's a good idea to make this function a bool function that returns "true" or an int function that returns any non-zero value. The AI can't do anything with the value that is returned from this function, but the xs-script-call Fact itself will return true. If you do need an AI to be able use an integer result from an XS function, you can use the xsSetGoal() or xsSetStrategicNumber() functions within an XS function to modify the value of a goal or SN, which the AI script can then check. Likewise, xsGetGoal() and xsGetStrategicNumber() functions can allow an XS function to get the current value of a goal or SN. If you call an XS function more than once, it's a good idea to defconst it (see the examples below). Otherwise, each time you call the function in the AI script it will add an entry to the string table. Here is some example .xs code which is used in the examples section below://This code is saved in a file called Example XS File.xs float max(float a = 0.0, float b = 2.0) { if(a > b) return (a); else return (b); } bool helloWorld() { xsChatData("Hello World"); return (true); } int rand() { int rand = xsGetRandomNumber(); //generates a random number between 0 and 32766 rand++; //increase random number range to between 1 and 32767 so that zero isn't returned, making a xs-script-call condition false xsSetGoal(510, rand); return (rand); }

[AIRef](https://airef.github.io/commands/commands-details.html#xs-script-call)

Completion insert text:

```text
(xs-script-call ${1:String})
```

