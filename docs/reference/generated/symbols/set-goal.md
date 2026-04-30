# `set-goal`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-set-goal"></a>

## `set-goal`

- Kind: `command`
- Detail: Action - Goals

Syntax: `(set-goal <GoalId> <Value>)`

Sets a given goal to a given value. While their purpose may be unclear based on their name, goals are variables which can store an integer value which can be checked with this command or with up-compare-goal. Each goal is given an ID, and AIs have 16000 goals available (only 512 in UP and only 40 in AoC) that they can use to store different values, and they all store the value -1 at the beginning of the game. Goals are one of the most important concepts of AI scripting, so it's good to learn how to use them. In programming speak, goals are a 16000-length one-indexed 32-bit integer array, pre-initialized to -1, and a GoalId refers to a particular index of that array. The set-goal command sets the value the given GoalId to the given integer value. New goals or variables cannot be defined, only constants (called defconsts by the AI engine), so AI scripters are limited to these 16000 goals, though unused strategic numbers can also be used like goals in a pinch. If the paragraph above makes absolutely no sense to you, you can imagine goals like a bank which holds 16000 bank accounts, numbered with IDs from 1 to 16000. These accounts can hold whole amounts (no cents or decimal amounts of money), and they can store either positive or negative amounts of money. These bank accounts are restricted to holding between -2,147,483,648 and 2,147,483,647 dollars, and they all start with -$1 (negative 1 dollars) stored inside them until they are used by a customer (the AI scripter). The set-goal and up-modify-goal commands can modify how much money is stored in a particular account. Following this bank metaphor, the goal command checks if the given bank account number holds the given amount of money. For example, (goal 5 13) checks if goal ID #5 holds the value 13 (i.e. bank account #5 holds $13), and (goal 415 -3274) checks if goal ID #415 holds the value -3,274 (i.e. bank account #415 holds -$3,274). You can also use up-compare-goal" to check the current value of a goal ID in a more powerful manner, such as checking if the goal stores greater or less than the given value. It is pretty common to use a defconst to refer to a goal ID number to make the AI more readable. See the second example below on what this looks like." cSetGoal.commandParameters = [ { nameLink: pGoalId.getLink(), name: "GoalId", type: "Const", dir: "in", range: "A valid GoalId, from 1 to 16000.", note: "The goal to set." }, { nameLink: pValue.getLink(), name: "Value", type: "Const", dir: "in", range: "-2,147,483,648 to 2,147,483,647.", note: "The value to set the goal to." } ]

[AIRef](https://airef.github.io/commands/commands-details.html#set-goal)

Completion insert text:

```text
(set-goal ${1:GoalId} ${2:Value})
```

