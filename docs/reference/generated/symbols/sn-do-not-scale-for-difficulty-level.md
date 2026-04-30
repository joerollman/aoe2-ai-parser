# `sn-do-not-scale-for-difficulty-level`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-do-not-scale-for-difficulty-level"></a>

## `sn-do-not-scale-for-difficulty-level`

- Kind: `strategic-number`
- Detail: SN 229 - Other

Disables the automatic difficulty-scaling. It is recommended to set this to 1 and do any difficulty adjustments manually. This needs to be issued BEFORE such SN's are altered or you'll see the values change by a set percentage. The default of 0 allows these SNs to be automatically changed when set using (set-strategic-number). There are differences between Scenarios and Non-Scenarios (thanks to scripter64 for testing this).Non-Scenario GameHard and Hardest:No changeModerate: multiplied by 0.75:archived-non-de-strategic-numberboatsEasy: multiplied by 0.5:same list as moderateEasiest: multiplied by 0.25:same list as moderateScenario GameHardest:No changeHard: multiplied by 0.8:archived-non-de-strategic-numberdistanceModerate: multiplied by 0.6:archived-non-de-strategic-numberdistanceEasy: multiplied by 0.4:same list as moderateEasiest: multiplied by 0.2:same list as moderate

Default: `0`

Required range: `0 to 1`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-do-not-scale-for-difficulty-level)

