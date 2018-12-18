var codeEditor = new CodeEditor();
var codeMirror = null;
var language = "Python";

function CodeEditor(){}

CodeEditor.prototype.initCodeEditor = function() {
    this.codeAreaTextArea = $( ".codemirror-text-area" );

    codeMirror = CodeMirror.fromTextArea(this.codeAreaTextArea[0], {
        mode: { name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        readOnly: false,
        showCursorWhenSelecting: true,
        lineNumbers: true,
        firstLineNumber: 1,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        matchBrackets: true,
        extraKeys: {"Tab": "indentMore",
            "Shift-Tab": "indentLess"},
    });

    codeMirror.setSize("100%", "100%");
}

CodeEditor.prototype.render = function(){
    if (workspace.isDragging()) return;
    this.renderEnforce();
}

CodeEditor.prototype.renderEnforce = function() {
    var code;
    switch(language){
        case "Python": {
            code = Blockly.Python.workspaceToCode(workspace);
            codeMirror.mode={ name: "python",
                version: 3,
                singleLineStringErrors: false
            };
            break;
        }
        case "Javascript": {
            code = Blockly.JavaScript.workspaceToCode(workspace);
            codeMirror.mode={ name: "javascript"};
            break;
        }
        case "XML": {
            code = Blockly.Xml.domToPrettyText(Blockly.Xml.workspaceToDom(workspace));
            codeMirror.mode={ name: "javascript"};
            break;
        }
    }
    codeMirror.setValue(code);
}

CodeEditor.prototype.setLanguage = function(lang){
    language = lang;
    this.renderEnforce();
}
