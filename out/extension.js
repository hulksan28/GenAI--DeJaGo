"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const fs = require("fs");
const vscode = require("vscode");
function extractContents(filePath, startWord) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    return new Promise((resolve, reject) => {
        fs.readFile(`${workspaceFolder}/${filePath}`, "utf8", (err, data) => {
            if (err) {
                reject(err);
            }
            else {
                const startIndex = data.indexOf(startWord);
                if (startIndex === -1) {
                    return "";
                }
                const delimiterIndex = data.indexOf("-----", startIndex);
                const extractedContent = data.slice(startIndex, delimiterIndex);
                resolve(extractedContent);
            }
        });
    });
}
function activate(context) {
    let hoverProvider = vscode.languages.registerHoverProvider("*", {
        async provideHover(document, position) {
            const range = document.getWordRangeAtPosition(position);
            const word = document.getText(range);
            try {
                const extractedContents = await extractContents("summary.txt", word);
                return new vscode.Hover(`Summary:\n${word}: ${extractedContents}\n`);
            }
            catch (err) {
                vscode.window.showErrorMessage(`Failed to read file: ${err}`);
            }
        },
    });
    let buildProjectSummary = vscode.commands.registerCommand("code-summarizer.buildProjectSummary", () => {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage("No workspace folder found.");
            return;
        }
        const buildCommand = "python summarizer.py";
        const terminal = vscode.window.createTerminal({
            cwd: workspaceFolder,
        });
        terminal.sendText(buildCommand);
        terminal.show();
    });
    context.subscriptions.push(hoverProvider);
    context.subscriptions.push(buildProjectSummary);
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map