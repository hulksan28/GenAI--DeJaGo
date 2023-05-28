# code-summarizer README

## Steps to run the extension

1. Navigate to **extension.ts** file in **src** folder.
2. Press F5 to run the extension.
3. A new extension development host vscode window will open.
4. Open the folder containing the project you want to summarize.
5. Copy **summarizer.py** file in **src** folder to the root folder that you just now opened in the extension development host window.
6. Press Ctrl+Shift+P and execute the command "Build Project Summary"
7. A new **summary.txt** file will be created in the root folder.
8. Now hover on the methods to see its summary.

**NOTE**: In **summarizer.py** remember to replace the OpenAI API Key value.
