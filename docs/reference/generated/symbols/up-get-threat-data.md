# `up-get-threat-data`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-get-threat-data"></a>

## `up-get-threat-data`

- Kind: `command`
- Detail: Action - Defense

Syntax: `(up-get-threat-data <ThreatTime> <ThreatPlayer> <ThreatSource> <ThreatTarget>)`

Get the elapsed time, player, source, and target of the last threat and store them in the four specified goals. This command returns the absolute, most recent attack information before the rule pass begins. If the last attack event was from a p2 archer against one of your villagers, you'll get "time, 2, 900, 904" in return (900 = archery-class, 904 = villager-class). In an epic battle, it would become relatively useless in determining what is going on.

[AIRef](https://airef.github.io/commands/commands-details.html#up-get-threat-data)

Completion insert text:

```text
(up-get-threat-data ${1:ThreatTime} ${2:ThreatPlayer} ${3:ThreatSource} ${4:ThreatTarget})
```

