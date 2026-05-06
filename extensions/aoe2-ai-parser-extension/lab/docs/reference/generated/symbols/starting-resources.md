# `starting-resources`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-starting-resources"></a>

## `starting-resources`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(starting-resources <compareOp> <StartingResources>)`

Checks the starting resources level. The standard setting is Low resources. In games without a Starting Resources option, like Death Match, starting-resources will be equal to 1 (low resources), probably because 1 is the standard resource setting in random map games. DE added the option for Ultra High, Infinite, and Random resource starts. Before DE, AIs on hardest difficulty would get 500 of each resource at the beginning of each age, including at the beginning of the game, but DE no longer does this. Starting resources can be modified by snAddStartingResourceWood, snAddStartingResourceFood, snAddStartingResourceGold, or snAddStartingResourceStone, though using these strategic numbers is considered cheating in AI tournaments. Starting resource amounts:Low Resources: start with 200W, 200F, 100G, and 200S.Medium Resources: start with 500W, 500F, 300G, and 400S.High Resources: start with 1000W, 1000F, 700G, and 800S.Ultra High Resources (DE only): start with 20,000W, 20,000F, 10,000G, and 5000S (same as Death Match).Infinite Resources (DE only): infinite amounts of each resource.Random Resources (DE only): start with random amounts of each resource.

[AIRef](https://airef.github.io/commands/commands-details.html#starting-resources)

Completion insert text:

```text
(starting-resources ${1:compareOp} ${2:StartingResources})
```

