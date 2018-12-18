var webSocketManager  = new WebSocketManager();
var socket = null;
var connected = false;
var isAttemptingToConnect = false;
var motorsAvailable = false;
var distanceSensorsAvailable = false;
var cameraAvailable = false;
var isRefreshing = false;


var STATE_CONNECTING = "connecting";
var STATE_CONNECTED = "connected";
var STATE_DISCONNECTED = "disconnected";


function WebSocketManager(){

}

WebSocketManager.prototype.initWebSocketManager = function() {
    webSocketManager.connect();
}

WebSocketManager.prototype.connect = async function(){
    return new Promise(function(resolve, reject) {
        isAttemptingToConnect = true;
        webSocketManager.setConnectionButtonState(STATE_CONNECTING);
        socket = new WebSocket("ws://" + location.hostname + ":8000/ws");
        socket.onopen = function () {
            webSocketManager.changeConnectedState(true);
            console.log('client side socket open');
            socket.send(JSON.stringify({"command": "ready"}));
            resolve();
        };
        socket.onerror = function (e) {
            piwarsRobot.displayMessage("Cannot connect to the server", 'error');
            reject();
        }
        socket.onmessage = function (message) {
            var msg = JSON.parse(message.data);

            if (msg['report'] === 'start_info') {
                connected = true;
                motorsAvailable = msg['motorsAvailable'];
                cameraAvailable = msg['cameraAvailable'];
            }
            else {
                codeRunner.handleWebsocketMessages(msg);
            }
        };
        socket.onclose = function (e) {
            console.log('client side socket onclose');
            socket = null;
            webSocketManager.changeConnectedState(false);
            isAttemptingToConnect = false;
        };
    });
}

WebSocketManager.prototype.sendMessage = function(msg) {
    if(socket!=null && connected){
        socket.send(msg);
    }
}

WebSocketManager.prototype.changeConnectedState = function(isConnected) {
    if(isConnected){
        connected = true;
        webSocketManager.setConnectionButtonState(STATE_CONNECTED);
    }
    else{
        connected = false;
        if(!isRefreshing) webSocketManager.setConnectionButtonState(STATE_DISCONNECTED);
        if(!isAttemptingToConnect){
            piwarsRobot.displayMessage("Server closed connection", 'error');
        }
    }
    codeRunner.handleConnectionStateChanged(isConnected);
}

WebSocketManager.prototype.refreshConnection = async function(){
    isRefreshing = true;
    webSocketManager.setConnectionButtonState(STATE_CONNECTING);
    if(socket !=null && connected){
        var msg = JSON.stringify({"command": "shutdown"});
        try {
            socket.send(msg);
            socket.close();
        }
        catch(e){

        }
        socket==null;
        connected=false;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
    webSocketManager.setConnectionButtonState(STATE_CONNECTING);
    isRefreshing = false;
    return webSocketManager.connect();
}

WebSocketManager.prototype.setConnectionButtonState = function(state){
    console.log('set state '+state);

    switch(state){
        case STATE_CONNECTED:
            $('#refreshConnectionButton').prop('disabled', false).removeClass('disabled').on("click");
            $('#refreshConnectionButton').off('click', webSocketManager.refreshConnection);
            $('#refreshConnectionButton').on('click', webSocketManager.refreshConnection);
            $('#refreshConnectionButton').removeClass('red');
            break;
        case STATE_DISCONNECTED:
            $('#refreshConnectionButton').prop('disabled', false).removeClass('disabled').on("click");
            $('#refreshConnectionButton').off('click', webSocketManager.refreshConnection);
            $('#refreshConnectionButton').on('click', webSocketManager.refreshConnection);
            $('#refreshConnectionButton').addClass('red');
            break;
        case STATE_CONNECTING:
            $('#refreshConnectionButton').removeClass('red');
            $('#refreshConnectionButton').prop('disabled', true).addClass('disabled').off( "click" );
            $('#refreshConnectionButton').on('click', webSocketManager.refreshConnection);
            break;

    }
}