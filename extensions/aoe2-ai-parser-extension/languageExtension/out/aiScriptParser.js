"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = require("fs");
const AiScriptErrorChecker_1 = require("./AiScriptErrorChecker");
const path_1 = require("path");
const url_1 = require("url");
var scp_open = ["(", ";", "\"", "#load-if-defined"];
var scp_close = [")", "\n", "\"", "#end-if"];
var AiScriptScopeType;
(function (AiScriptScopeType) {
    AiScriptScopeType[AiScriptScopeType["COMMENT"] = 0] = "COMMENT";
    AiScriptScopeType[AiScriptScopeType["LOAD_IF_DEFINED"] = 1] = "LOAD_IF_DEFINED";
    AiScriptScopeType[AiScriptScopeType["LOAD"] = 2] = "LOAD";
    AiScriptScopeType[AiScriptScopeType["LOAD_RANDOM"] = 3] = "LOAD_RANDOM";
    AiScriptScopeType[AiScriptScopeType["DEFCONST"] = 4] = "DEFCONST";
    AiScriptScopeType[AiScriptScopeType["DEFRULE"] = 5] = "DEFRULE";
    AiScriptScopeType[AiScriptScopeType["FACT"] = 6] = "FACT";
    AiScriptScopeType[AiScriptScopeType["ACTION"] = 7] = "ACTION";
})(AiScriptScopeType || (AiScriptScopeType = {}));
exports.AiScriptScopeType = AiScriptScopeType;
/******************************************************************/ /**
 * @class AiScriptParser
 * Capable of detecting certain errors
 **********************************************************************/
class AiScriptParser {
    logThis(value) {
        if (false) { // Set to false for release
            this.logger += value + "\n";
        }
    }
    /******************************************************************/ /**
     * Constructor
     * @param[in] aifile        Full path to a given '.ai' file
     * @param[in] parameters    AoE2 script parameters
     **********************************************************************/
    constructor(ainame, aidir, parameters) {
        // Set the top level filenames
        this._top_directory = aidir;
        this._aifile = path_1.join(aidir, ainame + '.ai');
        this._top_perfile = path_1.join(aidir, ainame + '.per');
        this._std_aoe2pars = parameters;
        // Clear everything
        this.reset();
    }
    ;
    /******************************************************************/ /**
     * Clears list of files to be parsed
     **********************************************************************/
    clearFiles() {
        this._perfiles = [];
    }
    ;
    /******************************************************************/ /**
     * Parse files to build a list of errors in the files
     **********************************************************************/
    filesToParse() {
        // Loop through all files and locate the other loads
        return this._perfiles;
    }
    ;
    /******************************************************************/ /**
     * Search for all files that need to be loaded
     * @param[in] filepath      Path to top file to begin searching loaded files
     **********************************************************************/
    findFiles(filepath) {
        // Load the file
        let text = fs_1.readFileSync(filepath, 'utf8');
        // Get all of the files loaded by this file
        let load_regex = /\(\s*load(-random){0,1}[\s\S]+[^\(\)][\s\S]+\)/g;
        let file_regex = /\"[^\"]+\"/g;
        // Loop through all of these files
        let m;
        while (m = load_regex.exec(text)) {
            // Extract the filename, note here that if using load-random
            // there may be multiple files in the 
            let file_match;
            while (file_match = file_regex.exec(m[0])) {
                // Remove the leading and trailing quotes
                let file_name = file_match[0];
                file_name = file_name.substr(1, file_name.length - 2);
                // Only search the file if it hasn't already been loaded
                if (this._perfiles.indexOf(file_name) == -1) {
                    this._perfiles.push(file_name);
                    this.findFiles(file_name);
                }
            }
        }
    }
    ;
    /**
     * Returns a list of constants defined by the AI
     */
    //getDefconsts(filepath?: null | string): void;
    /**
     * Returns a list of errors in the file defined by the AI
     */
    // getErrors(script_text: string, maxErrors: number=10000): AiScriptErr[] {
    //     let errorChecker: AiScriptErrorChecker = new AiScriptErrorChecker(this._std_aoe2pars);
    //     let errors: AiScriptErr[] = errorChecker.runErrorChecker(script_text, maxErrors);
    //     return errors;
    // }
    getErrors() {
        return this._ai_errors;
    }
    /************************************************************/ /**
     * UPDATED FUNCTIONS
     ****************************************************************/
    /**
     * Get the correct string for a file path on any system
     */
    filepath(relative_path) {
        let filepath = this._top_directory;
        relative_path.split("\\").forEach(dirname => {
            filepath = path_1.join(filepath, dirname);
        });
        return filepath;
    }
    /**
     * Clears all existing stored information about the AI script
     */
    reset() {
        this._scopes = [];
        this._ai_scopes = new Map();
        this._ai_errors = [];
        this._passed_scopes = new Map();
        this._cur_file = [];
    }
    /**
     * Parse the entire AI (just calls parseFile on main '.per' file)
     */
    parse() {
        // Clear the scopes and errors
        this.reset();
        this.logThis("START OF LOGGING:");
        // Parse the script
        this.parseFile(this._top_perfile, this._scopes);
        // Make sure all scopes are closed
        this._scopes.forEach(scope => {
            this._ai_errors.push(AiScriptErrorChecker_1.AiScriptErrorChecker.getScopeError(scope));
        });
        this.logThis("STOP LOGGING");
    }
    /**
     * Parse a given file
     */
    parseFile(filename, active_scopes) {
        this.logThis("parsing file: " + filename);
        // Append the file to the list and create an entry in 'passed_scopes'
        this._cur_file.push(filename);
        this._passed_scopes[filename] = active_scopes;
        this._ai_scopes[filename] = [];
        let url = new url_1.URL(filename);
        let text = fs_1.readFileSync(url, 'utf8');
        this.parseCode(text, 0, active_scopes);
        // Remove the file
        this._cur_file.pop();
        // TODO: If there are no defrule scopes in the file, generate an error
    }
    /**
     * Parse a given section of code
     */
    parseCode(code, indx_offset, active_scopes) {
        let incomment = false; // current comment status
        let indx = -1; // index in the 'code' string
        let c = undefined; // Current character
        let err = undefined; // An error
        let enforce_close = false; // Produces an error if we try to open
        // another scope when 'enforce_close' = true
        let closings = [];
        let scopes = [];
        // Loop through all characters
        while (++indx < code.length) {
            c = code[indx];
            // Only parse if not in a comment
            if (!incomment) {
                if (c === ";") {
                    incomment = true;
                }
                else if ((closings.length > 0) && (c === closings[closings.length - 1])) {
                    // Close the current scope
                    let scope = scopes[scopes.length - 1];
                    scope.stop = indx + indx_offset;
                    this._ai_scopes[scope.filename].push(scope);
                    this.parseScope(code.substring(scope.start, scope.stop), scopes);
                    scopes.pop();
                    closings.pop();
                    enforce_close = false;
                }
                // Check if we're starting a new scope
                else if (c === "(") {
                    /* defconst */
                    if (code.substr(indx, 9) === "(defconst") {
                        this.logThis("defconst encountered");
                        // We've found a defconst
                        scopes.push({
                            filename: this._cur_file[this._cur_file.length - 1],
                            type: AiScriptScopeType.DEFCONST,
                            start: indx + 1 + indx_offset,
                            stop: indx + 1 + indx_offset
                        });
                        closings.push(")");
                        enforce_close = true;
                    }
                    /* defrule */
                    /* load */
                    else if (code.substr(indx, 6) === "(load ") {
                        this.logThis("load encountered");
                        // We've found a defconst
                        scopes.push({
                            filename: this._cur_file[this._cur_file.length - 1],
                            type: AiScriptScopeType.LOAD,
                            start: indx + 1 + indx_offset,
                            stop: indx + 1 + indx_offset
                        });
                        closings.push(")");
                        enforce_close = true;
                    }
                    /* load-random */
                    else if (code.substr(indx, 12) === "(load-random") {
                        this.logThis("load-random encountered");
                        // We've found a defconst
                        scopes.push({
                            filename: this._cur_file[this._cur_file.length - 1],
                            type: AiScriptScopeType.LOAD_RANDOM,
                            start: indx + 1 + indx_offset,
                            stop: indx + 1 + indx_offset
                        });
                        closings.push(")");
                        enforce_close = true;
                    }
                }
            }
            // ... indentify when we've finished the comment
            else if (c === "\n") {
                incomment = false;
            }
        }
    }
    parseScope(code, active_scopes) {
        let scope = active_scopes[active_scopes.length - 1];
        switch (scope.type) {
            case AiScriptScopeType.DEFCONST:
                this.parseDefconst(code, scope.start);
                break;
            case AiScriptScopeType.FACT:
                this.parseFact(code, scope.start, active_scopes);
                break;
            case AiScriptScopeType.ACTION:
                this.parseAction(code, scope.start, active_scopes);
                break;
            case AiScriptScopeType.DEFRULE:
                this.parseDefrule(code, scope.start, active_scopes);
                break;
            case AiScriptScopeType.LOAD:
                this.parseLoad(code, scope.start, active_scopes);
                break;
            case AiScriptScopeType.LOAD_RANDOM:
                this.parseLoadRandom(code, scope.start, active_scopes);
                break;
            case AiScriptScopeType.LOAD_IF_DEFINED:
                this.parseCode(code, scope.start, active_scopes);
                break;
        }
        return "";
    }
    parseDefconst(code, offset) {
        this.logThis("parsing defconst: " + code);
        let space = { left: 0, right: 0 };
        code = this.trim_code(code, space); // trim white space from front and back
        let defconst_vals = code.split(/\s+/g);
        // Throw error if there are too many parameters
        if (defconst_vals.length > 3) {
            Error;
        }
    }
    parseDefrule(code, offset, active_scopes) {
    }
    parseFact(code, offset, active_scopes) {
    }
    parseAction(code, offset, active_scopes) {
    }
    parseLoad(code, offset, active_scopes) {
    }
    parseLoadRandom(code, offset, active_scopes) {
    }
    trim_code(code, space) {
        let trimmed = code.trimLeft();
        space.left = code.length - trimmed.length;
        trimmed = trimmed.trimRight();
        space.right = code.length - trimmed.length - space.left;
        return trimmed;
    }
    getScopes() {
        return this._ai_scopes;
    }
}
exports.AiScriptParser = AiScriptParser;
;
//# sourceMappingURL=aiScriptParser.js.map