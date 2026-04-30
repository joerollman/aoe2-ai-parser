# `log`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-log"></a>

## `log`

- Kind: `command`
- Detail: Action - Debugging

Syntax: `(log <String>)`

Writes the given string to a log file. Used purely for testing purposes. Works only if logging is enabled. Logging is disabled in AoC (the old CD version of the game) and Userpatch. Use up-log-data instead. However, logging can be enabled in DE. To do this, you need to launch the game with the parameters LOGSYSTEMS=AIScript and VERBOSELOGGING (case sensitive). To do this with the Steam version, open your Steam games library with the Steam client, right click on Age of Empires II: Definitive Edition in the left sidebar that lists the games you own, and click Properties. In the Properties window, under the General tab, type the parameters above separated by spaces. Then, when you launch the game these parameters will be active. The log produced in DE will be found in the Steam user folder, usually something like "C:\Users\[user ID]\Games\Age of Empires 2 DE\logs" but note that this log isn't just used by the AI (it would be best to log something identifying the AI log at the start of the game), some of these logs with VERBOSELOGGING can get quite large so it might be a good idea to periodically clean out the folder.

[AIRef](https://airef.github.io/commands/commands-details.html#log)

Completion insert text:

```text
(log ${1:String})
```

