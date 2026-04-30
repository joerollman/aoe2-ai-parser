# `defconst`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-defconst"></a>

## `defconst`

- Kind: `command`
- Detail: Other - Other

Syntax: `(defconst <Defconst> <Value>)`

Creates a user-defined constant. The syntax of the AI expert system (the programming language that AoE2 uses for its computer AIs) is entirely based on a dictionary of constants (text variables that are assigned a value that will remain constant) that have an integer or string (text) that are assigned to them. For example, "archer" is a constant that is internally defined with the value 4, which is the archer's ID number in the game's unit list. So, any AI code that uses the constant "archer" will interpret it as the number 4. For example, (unit-type-count archer > 5) will check if the AI has more than 5 units with the Unit ID #4, thus counting the number of archers the AI has. The AoE2 AI engine allows AI scripters to define custom constants with the defconst command. Constants are very handy for naming of goals, goal values, timers, taunts, etc. Without constants all of these would be just nameless numbers. Unlike most commands, the defconst command must be used outside of a rule. During the first initial script pass, the AI engine will compile a list of all loaded defconsts and store their assigned values in memory, and the defconst lines in the code will be ignored for the rest of the game. All uses of that defconst must occur after the defconst line in your code, so the best practice is to include all of your defconsts at the top of your main AI file so that they are easy to find and maintain. If you group all of your defconsts together in one file, it makes it easy to customize your AI by changing the number that the defconst represents without having to change it everywhere in your file. In the example below, if you referred to num-dark-age-villagers in many places in your AI, you could easily change the defconst to be 12 villagers by changing it in just one place. If you want to assign a defconst to a different value depending on the game, you can put the defconst inside of a #load-if-defined or a #load-if-not-defined section. Only defconsts within a #load-if-defined or #load-if-not-defined that matches the current game settings will load and create that defconst. In DE, if you have more than one loaded defconst command with the same defconst name, the value of the last defconst with the same name will be the final value for that defconst. In UP, having multiple loaded defconsts with the same name will cause an error. Also, all defconsts used anywhere in the AI must have a defconst that is loaded for all game settings, even if that defconst is only used inside a #load-if-defined or #load-if-not-defined section of code that isn't loaded for the particular game. For example, if "num-eagle-warriors" is a defconst that is only used in code that is loaded with an American civ, the num-eagle-warriors defconst must be created for every possible game setting. For more information, there is a multi-part article series about defconsts here: Defconsts, Goals, and SNs.

[AIRef](https://airef.github.io/commands/commands-details.html#defconst)

Completion insert text:

```text
(defconst ${1:Defconst} ${2:Value})
```

