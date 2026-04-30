# `sn-profiling-threshold`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-profiling-threshold"></a>

## `sn-profiling-threshold`

- Kind: `strategic-number`
- Detail: SN 305 - Other

The maximum number of milliseconds between script passes before the game will be stopped and the debug screen will appear. Ignored if set to -1 (the default). For this SN to work, you must also add the Steam launch parameters AIDEBUGGING and AISCRIPTPROFILING. To set launch parameters, open Steam => Right click the game in the Library view => click Properties => and type the launch parameters, separated by spaces (not commas). According to offwo, the DE devs give a rough guideline that this shouldn't trigger at 1000 and under 600 was ideal, but offwo suggests that setting this SN to 1500-2000 is fine for a custom AI. Setting this SN to a higher value like 10000 can help find jump freezes too without having to wait a long time.

Default: `-1`

Required range: `Min to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-profiling-threshold)

