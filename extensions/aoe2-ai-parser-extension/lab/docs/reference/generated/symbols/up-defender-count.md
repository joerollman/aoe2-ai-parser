# `up-defender-count`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-defender-count"></a>

## `up-defender-count`

- Kind: `command`
- Detail: Fact - Counting, Defense, Units

Syntax: `(up-defender-count <compareOp> <Value>)`

Check the number of units actively defending in town. With this command you can check to see if your TSA attack is actually actively targeting anything or if it's just idling. If, after expecting your new town-size to initiate a defensive attack, the response from this command is far less than expected for several consecutive turns, your target may be unreachable by the defensive targeting system (target has been walled for protection by one of their allies, etc.) and you may need to switch targets.

[AIRef](https://airef.github.io/commands/commands-details.html#up-defender-count)

Completion insert text:

```text
(up-defender-count ${1:compareOp} ${2:Value})
```

