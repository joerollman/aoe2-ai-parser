# `defrule`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-defrule"></a>

## `defrule`

- Kind: `command`
- Detail: Other - Other

Syntax: `(defrule)`

Defines the start of a new rule. "defrule" is short for "define rule." Rules are the basis for the Expert System, the AI scripting language for AoE2. There is a list of things we know about the game world, the other players, and so on. These are called facts. We check the facts with rules until a set of conditions exists that we need the computer player to act upon. Actions are what we call those commands that cause things to happen in the game. Examples might be training a unit, researching a technology, or sending a chat message. Rules are defined in the script with the defrule instruction. Each defined rule is given a rule ID. If the conditions (facts) for the rule are met (i.e. true), the instructions in that rule (actions) are followed. If the conditions for the rule are not met (False), the rule is passed by. The facts section of the rule is separated from the following actions section with a "=>" forward arrow. Note that the parentheses around the rule are required, though the white-space formatting (spaces, tabs, etc.) is not important. Rules continue to be evaluated in order each pass unless they are disabled. This is done with the disable-self command. Disabled rules cannot be enabled later, but their rule ID is still valid, so the rule will still be counted for rule jump commands like up-jump-rule. Each rule must have at least one fact and at least one action. Each rule is limited to 32 commands, including facts, actions, and logical operators, such as and or not. In UP and the original versions of the game, rules were limited to 16 commands. AIs are limited to loading 10,000 rules. This limit does not include rules that aren't loaded for the particular game, such as rules within a #load-if-defined or a #load-if-not-defined block.

[AIRef](https://airef.github.io/commands/commands-details.html#defrule)

Completion insert text:

```text
(defrule)
```

