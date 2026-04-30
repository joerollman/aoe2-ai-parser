# `civ-selected`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-civ-selected"></a>

## `civ-selected`

- Kind: `command`
- Detail: Fact - Own Player Info

Syntax: `(civ-selected <Civ>)`

Checks the computer player's civilization. You can use "my-civ," which will automatically detect the civilization the AI is playing as. Note that the civilization names used with this command for pre-DE civs are usually different than the civ's display name. They are like the pLoadIfSymbol civ names where they often use the adjective form of the civ name, not the plural name. See pCiv for a list of correct civ names to use with this command. You can also enclose code in a #load-if-defined [CIV-NAME]-CIV block if it should only run when a particular civ is selected. To check for the civilization of other players, use players-civ.

[AIRef](https://airef.github.io/commands/commands-details.html#civ-selected)

Completion insert text:

```text
(civ-selected ${1:Civ})
```

