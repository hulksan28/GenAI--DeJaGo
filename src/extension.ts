import * as fs from "fs";
import * as vscode from "vscode";

function extractContents(filePath: string, startWord: string): Promise<string> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    return new Promise((resolve, reject) => {
        fs.readFile(`${workspaceFolder}/${filePath}`, "utf8", (err, data) => {
            if (err) {
                reject(err);
            } else {
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

export function activate(context: vscode.ExtensionContext) {
    let hoverProvider = vscode.languages.registerHoverProvider("*", {
        async provideHover(document, position) {
            const range = document.getWordRangeAtPosition(position);
            const word = document.getText(range);
            try {
                const extractedContents = await extractContents(
                    "summary.txt",
                    word
                );

                return new vscode.Hover(
                    `Summary:\n${word}: ${extractedContents}\n`
                );
            } catch (err) {
                vscode.window.showErrorMessage(`Failed to read file: ${err}`);
            }
        },
    });

    let buildProjectSummary = vscode.commands.registerCommand(
        "code-summarizer.buildProjectSummary",
        () => {
            const workspaceFolder =
                vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

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
        }
    );

    context.subscriptions.push(hoverProvider);
    context.subscriptions.push(buildProjectSummary);
}

export function deactivate() {}
