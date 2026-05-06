"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const aiScriptResources_1 = require("./aiScriptResources");
const aiScriptParser_1 = require("./aiScriptParser");
;
/******************************************************************/ /**
 * @function AiScriptErrCommandInvalid
 * Function to generate an error
 **********************************************************************/
function AiScriptErrDefine(position, severity, messageShort, messageLong) {
    return {
        severity: severity,
        filename: "unknown",
        code: 0,
        message: {
            short: messageShort,
            long: (messageLong !== undefined) ? messageLong : messageShort
        },
        position: {
            start: position.start,
            stop: position.stop
        }
    };
}
;
/******************************************************************/ /**
 * @function AiScriptErrCommandInvalid
 * Error when a command is unknown
 **********************************************************************/
function AiScriptErrCommandInvalid(position, messageShort, messageLong) {
    let err = AiScriptErrDefine(position, 1, messageShort, messageLong);
    err.code = 2003;
    return err;
}
exports.AiScriptErrCommandInvalid = AiScriptErrCommandInvalid;
;
/******************************************************************/ /**
 * @function AiScriptErrParamInvalidCount
 * Error when a parameter to a command is incorrect
 **********************************************************************/
function AiScriptErrParamInvalidCount(position, messageShort, messageLong) {
    let err = AiScriptErrDefine(position, 1, messageShort, messageLong);
    err.code = 2004;
    return err;
}
/******************************************************************/ /**
 * @function AiScriptErrIndentifierInvalid
 * Error when a parameter to a command is incorrect
 **********************************************************************/
function AiScriptErrIndentifierInvalid(position, messageShort, messageLong) {
    let err = AiScriptErrDefine(position, 1, messageShort, messageLong);
    err.code = 2005;
    return err;
}
/******************************************************************/ /**
 * @class AiScriptErrorChecker
 * Runs checks for all files
 **********************************************************************/
class AiScriptErrorChecker {
    /**
     * Constructs the error checker
     * @param[in] params        List of known aoe2 commands/identifiers
     */
    constructor(params) {
        this._params = params;
    }
    /**
     * Returns a full list of errors
     */
    runErrorChecker(scriptText, maxErrors = 10000) {
        // List of errors that will be extended as we go
        let errors = [];
        // Command related errors
        errors = errors.concat(this.checkCommands(scriptText, maxErrors));
        return errors;
    }
    //=========================================
    // Methods that check for specific errors
    //=========================================
    checkCommand(ruleText) {
        let errors = [];
        return errors;
    }
    ;
    checkFacts(commandText) {
        let errors = [];
        return errors;
    }
    checkActions(commandText) {
        let errors = [];
        return errors;
    }
    /**
     * Check for all command related errors
     */
    checkCommands(scriptText, maxErrors = 10000) {
        let errors = [];
        // Regex for finding commands
        let command_pattern = /(\(\s*)\w[^\(\)]*(\".*\")*[^\(\)]*(?=\s*\))/g;
        // Search the script text
        let m;
        while ((m = command_pattern.exec(scriptText)) && (errors.length < maxErrors)) {
            // Check if we're in a comment
            if (AiScriptErrorChecker.isComment(scriptText, m.index)) {
                continue;
            }
            // Get the command text, stripping the leading paren and any spaces after it
            let test_str = m[0].slice(m[1].length);
            // Search for matching command
            let right_pad = m[1].length;
            if (m.length > 2)
                test_str = test_str.replace(/\"[\s\S]*\"/g, 'STRING');
            // Replace strings with a single word, for ease of parsing
            let test_arr = test_str.split(/\s+/g);
            let test_com = test_arr[0];
            let com_match = this._params["Control"].values[test_com];
            if (com_match === undefined)
                com_match = this._params["Fact"].values[test_com];
            if (com_match === undefined)
                com_match = this._params["Action"].values[test_com];
            if (com_match === undefined)
                com_match = this._params["FactAction"].values[test_com];
            // Define the default command start/stop positions
            let pos = {
                start: m.index + right_pad,
                stop: m.index + m[0].length
            };
            // Run checks on the match
            if (com_match === undefined) {
                // Failure to find a match for the command
                pos.stop = pos.start + test_arr[0].length;
                let errMsg = "Unknown command `" + test_arr[0] + "`.";
                let best_guess = aiScriptResources_1.guessParam(test_arr[0], ["Fact", "Action"], this._params).guess;
                if (best_guess.length > 0) {
                    errMsg += " Did you mean: " + best_guess.join(', ');
                }
                errors.push(AiScriptErrCommandInvalid(pos, errMsg));
            }
            // ... check there are no parameters when there shouldn't be
            else if (com_match.pars === undefined) {
                if (test_arr.length > 1) {
                    let message = "Incorrect number of arguments to " +
                        "`" + test_arr[0] + "` " + "(expected 0" +
                        " but got " + (test_arr.length - 1) + ")";
                    pos.start = pos.start + test_arr[0].length + 1;
                    let err = AiScriptErrParamInvalidCount(pos, "Expected 0 arguments", message);
                    errors.push(err);
                }
            }
            // ... check we have the correct number of arguments
            else if ((com_match.pars.length !== test_arr.length - 1)) {
                let message = "Incorrect number of arguments to " +
                    "`" + test_arr[0] + "` " +
                    "(expected " + com_match.pars.length +
                    " but got " + (test_arr.length - 1) + ")";
                pos.start = pos.start + test_arr[0].length + 1;
                let err = AiScriptErrParamInvalidCount(pos, "Incorrect number of arguments", message);
                errors.push(err);
            }
            // ... Check the individual parameters are valid
            else {
                // Check all parameters are of correct type
                for (let i = 1; i < test_arr.length; ++i) {
                    // Offset the position values
                    pos.start += test_arr[i - 1].length + 1;
                    pos.stop = pos.start + test_arr[i].length;
                    // Get the expected parameter type and parameter
                    let expected = com_match.pars[i - 1].type;
                    let parValue = test_arr[i];
                    let parObj = aiScriptResources_1.findParam(this._params, parValue);
                    // Check type is valid
                    if (this._params[expected] === undefined) {
                        let message = "Unkown parameter type encountered: " +
                            "`" + expected + "`\n" +
                            "This is probably a bug in the extension, please report it!";
                        let err = AiScriptErrDefine(pos, 2, message);
                    }
                    // Check if the parameter is of valid type
                    else if (!aiScriptResources_1.InheritsFrom(parValue, expected, this._params)) {
                        let message = "Expected parameter of type " +
                            "`" + expected + "`. Value `" + parValue + "` invalid.";
                        let best_guess = aiScriptResources_1.guessParam(test_arr[0], [expected], this._params).guess;
                        if (best_guess.length > 0) {
                            message += " Did you mean: " + best_guess.join(', ');
                        }
                        let err = AiScriptErrIndentifierInvalid(pos, "Invalid parameter", message);
                        errors.push(err);
                    }
                    // Check if the parameter needs to be defined
                    else if ((parObj !== undefined) && (parObj.defined === false)) {
                        let message = "Friendly reminder that this parameter " +
                            "must be defined by you in a dedicated " +
                            "`defconst` before it is used.";
                        let err = AiScriptErrDefine(pos, 3, message);
                        errors.push(err);
                    }
                }
            }
        }
        return errors;
    }
    ;
    static isComment(scriptText, index) {
        while (scriptText[index--] !== "\n") {
            if (scriptText[index] === ";")
                return true;
        }
        // Made it to the start of the line
        return false;
    }
    static getScopeError(scope) {
        let scope_type = aiScriptParser_1.AiScriptScopeType[scope.type];
        // Define messgae and error position
        let msg = "Unclosed '" + scope_type + "' scope";
        let pos = { start: scope.start,
            stop: scope.start + scope_type.length };
        let err = AiScriptErrDefine(pos, 1, msg);
        err.filename = scope.filename;
        // Return the associated error
        return err;
    }
}
exports.AiScriptErrorChecker = AiScriptErrorChecker;
;
//# sourceMappingURL=aiScriptErrorChecker.js.map