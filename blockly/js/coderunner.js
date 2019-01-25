var codeRunner = new CodeRunner();
var latestCode = null;
var worker = null;
var workerTemplate = null;
var isRunning = false;
var isSimulation = false;

function CodeRunner(){}

CodeRunner.prototype.initCodeRunner = function() {
    var workerTemplateRequest = new XMLHttpRequest();
    workerTemplateRequest.open("GET", "http://"+location.hostname+":8000/blockly/js/workerTemplate.js", true);
    workerTemplateRequest.setRequestHeader('cache-control', 'no-cache, must-revalidate, post-check=0, pre-check=0');
    workerTemplateRequest.setRequestHeader('cache-control', 'max-age=0');
    workerTemplateRequest.setRequestHeader('expires', '0');
    workerTemplateRequest.setRequestHeader('expires', 'Tue, 01 Jan 1980 1:00:00 GMT');
    workerTemplateRequest.setRequestHeader('pragma', 'no-cache');
    workerTemplateRequest.onreadystatechange = function() {
        if (workerTemplateRequest.readyState === 4) {  // Makes sure the document is ready to parse.
            if (workerTemplateRequest.status === 200) {  // Makes sure it's found the file.
                workerTemplate = workerTemplateRequest.responseText;
            }
        }
    }
    workerTemplateRequest.send(null);
}

CodeRunner.prototype.runCodeButtonHandler = function() {
    if(!connected){
        $('#runButton').attr("disabled", "disabled");
        webSocketManager.connect().then(function(){
            codeRunner.runCode(false);
        }).catch(function(exc){
            piwarsRobot.displayMessage(exc, "error");
        }).finally(function(){
            $('#runButton').removeAttr("disabled");
        });
    }
    else {
        codeRunner.runCode(false);
    }
}

CodeRunner.prototype.runSimulationButtonHandler = function() {
    codeRunner.runCode(true);
}


CodeRunner.prototype.runCode = function(setSimulation) {
    if(!codeRunner.checkCodeIsValid()){
        return;
    }
    var prefix = Blockly.JavaScript.STATEMENT_PREFIX;
    Blockly.JavaScript.STATEMENT_PREFIX = 'highlightBlock(%1);\n';
    var reserved  = Blockly.JavaScript.RESERVED_WORDS_;
    Blockly.JavaScript.addReservedWords('highlightBlock');
    Blockly.JavaScript.addReservedWords('runBlocklyCode');
    Blockly.JavaScript.addReservedWords('alert');
    Blockly.JavaScript.addReservedWords('sleep');
    Blockly.JavaScript.addReservedWords('robot_drive');
    Blockly.JavaScript.addReservedWords('robot_stop');
    Blockly.JavaScript.addReservedWords('robot_set_camera_mode');
    Blockly.JavaScript.addReservedWords('robot_get_list_of_alien_ids');
    Blockly.JavaScript.addReservedWords('robot_get_distance_to_alien');
    Blockly.JavaScript.addReservedWords('robot_get_x_angle_to_alien');
    Blockly.JavaScript.addReservedWords('robot_get_y_angle_to_alien');
    Blockly.JavaScript.addReservedWords('robot_get_list_of_coloured_sheets');
    Blockly.JavaScript.addReservedWords('robot_get_distance_to_a_coloured_sheet');
    Blockly.JavaScript.addReservedWords('robot_get_x_angle_to_a_coloured_sheet');
    latestCode = Blockly.JavaScript.workspaceToCode(workspace);
    Blockly.JavaScript.STATEMENT_PREFIX = prefix;
    Blockly.JavaScript.RESERVED_WORDS_=reserved;
    // Build a worker from an anonymous function body
    var blob = new Blob([workerTemplate.replace("//%BlocklyCode%//",latestCode),
    ], { type: 'application/javascript' } );
    var blobURL = URL.createObjectURL(blob);
    worker = new Worker(blobURL);
    worker.addEventListener('message', codeRunner.handleWorkerMessages);
    worker.addEventListener('error', function(event){
        piwarsRobot.displayMessage(event.message, 'error');
    });
    isRunning=true;
    isSimulation=setSimulation;
    codeRunner.setRunningUI();
    webSocketManager.sendMessage(JSON.stringify({"command": 'startRun', 'isSimulation': isSimulation}));
    if(showMap){
        mapVisualiser.showVisualisation(isSimulation);
    }
    worker.postMessage('start');

    // Won't be needing this anymore
    URL.revokeObjectURL(blobURL);
}

CodeRunner.prototype.handleWorkerMessages = function(event){
    switch(event.data.message){
        case 'error':
            piwarsRobot.displayMessage(event.data.data, 'error');
            codeRunner.stopCode();
            break;
        case 'highlightBlock':
            codeRunner.highlightBlock(event.data.id);
            break;
        case 'alert':
            piwarsRobot.displayMessage(event.data.msg);
            break;
        case 'serverCall':
            webSocketManager.sendMessage(event.data.msg);
            break;
        case 'finished':
            piwarsRobot.displayMessage("Finished", 'system');
            codeRunner.stopCode();
            break;
    }
}

CodeRunner.prototype.handleConnectionStateChanged = function(isConnected){
    if(!isConnected && isRunning){
        codeRunner.stopCode();
    }
}

CodeRunner.prototype.handleWebsocketMessages = function(msg) {
    if(worker==null || !isRunning) return;
    switch(msg.message) {
        case 'updateAlienReadings':
            worker.postMessage(msg);
            if(msg.aliens==null||msg.aliens.length==0){
                $('#sensorsReport')[0].innerHTML='No aliens';
            }
            else{
                var aliens="";
                for(i=0;i<msg.aliens.length;i++){
                    aliens=aliens+'ID:'+msg.aliens[i]['id']+' Distance:'+msg.aliens[i]['distance'];
                }
                $('#sensorsReport')[0].innerHTML=aliens;
            }
            break;
        case 'updateColouredSheetsReadings':
            worker.postMessage(msg);
            if(msg.sheets==null||msg.sheets.length==0){
                $('#sensorsReport')[0].innerHTML='No coloured sheets';
            }
            else{
                var sheets="";
                for(i=0;i<msg.sheets.length;i++){
                    sheets=sheets+' '+msg.sheets[i]['colour']+':'+msg.sheets[i]['distance'];
                }
                $('#sensorsReport')[0].innerHTML=sheets;
            }
            break;
    }
}

CodeRunner.prototype.stopCodeButtonHandler = function () {
    piwarsRobot.displayMessage("Code stopped", 'system');
    codeRunner.stopCode();
}

CodeRunner.prototype.stopCode = function () {
    if(worker != null){
        worker.terminate();
        worker = null;
    }
    webSocketManager.sendMessage(JSON.stringify({"command": 'stopRun'}));
    codeRunner.resetUi();
    isRunning = false;
    isSimulation = false;
}


CodeRunner.prototype.highlightBlock = function (id) {
    workspace.highlightBlock(id);
}

CodeRunner.prototype.setRunningUI = function() {
    $('#runButton').hide();
    //$('#simulateButton').hide();
    //$('#driveButton').hide();
    //$('#mapButton').hide();
    $('#stopButton').show();
}

CodeRunner.prototype.resetUi = function() {
    workspace.highlightBlock(null);
    $('#runButton').show();
    //$('#simulateButton').show();
    //$('#driveButton').show();
    //$('#mapButton').show();
    $('#stopButton').hide();
    mapVisualiser.stopVisualisation();
}

CodeRunner.prototype.checkCodeIsValid = function() {
    var hasErrors = false;
    var allBlocks = workspace.getAllBlocks();
    //check for unconnected values or variables
    for(var i=0; i< allBlocks.length; i++){
        allBlocks[i].setHighlighted(false);
        if(allBlocks[i].outputConnection !=null && allBlocks[i].outputConnection.targetConnection == null){
            allBlocks[i].setHighlighted(true);
            hasErrors = true;
        }
    }
    workspace.render();
    if(hasErrors){
        piwarsRobot.displayMessage('Error: Your code has unconnected values, statements or variables (see highlighted).', 'error');
        setTimeout(function(){
            codeRunner.unhighlightAll();
        }, 5000);
        return false;
    }

    //check that there is no more than one entry to the program
    var entryBlocks = new Array();
    for(var i=0; i< allBlocks.length; i++) {
        if(allBlocks[i].previousConnection != null && allBlocks[i].previousConnection.targetConnection == null){
            entryBlocks.push(allBlocks[i]);
        }
    }
    if(entryBlocks.length==0){
        piwarsRobot.displayMessage('Error: There are no statements in your code', 'error');
       return false;
    }
    else if(entryBlocks.length>1){
        for(j=0;j<entryBlocks.length;j++){
            entryBlocks[j].setHighlighted(true);
        }
        piwarsRobot.displayMessage('Error: There are multiple entry statements in your code (see highlighted).', 'error');
        setTimeout(function(){
            codeRunner.unhighlightAll();
        }, 5000);
        return false;
    }
    return true;
}

CodeRunner.prototype.unhighlightAll = function() {
    var allBlocks = workspace.getAllBlocks();
    for(var i=0; i< allBlocks.length; i++) {
        allBlocks[i].setHighlighted(false);
    }
}

