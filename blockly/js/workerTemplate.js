var window = new WindowStub();
var running = false;
var lastMarkers = null;

var lastDriveParams = null;
var lastTurnParams = null;

function WindowStub(){

}

WindowStub.prototype.alert = function(msg){
    self.postMessage({"message":"alert", "msg":msg});
}

self.onmessage = function(e) {
   if(e.data=='start'){
       runBlocklyCode();
   }
   else if(e.data.message=='updateMarkerReadings'){
       lastMarkers = e.data['markers'];
   }
}

async function runBlocklyCode(){
    try{
        running = true;
        await blocklyCodeWrapper();
    }
    catch(e){
        self.postMessage({"message":"error", "data":e.toString()});
    }
    finally{
        running = false;
        self.postMessage({"message":"finished"});
    }
}

async function blocklyCodeWrapper(){
    //%BlocklyCode%//
}


function highlightBlock(id){
    self.postMessage({"message":"highlightBlock", "id":id});
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

function robot_drive(speedLeft, speedRight) {
    if(lastDriveParams!=null && lastDriveParams.speedLeft == speedLeft && lastDriveParams.speedRight == speedRight){
        return;
    }
    else{
        lastDriveParams = {'speedLeft':speedLeft, 'speedRight':speedRight}
    }
    var msg = {"command": 'drive', 'speedLeft': speedLeft, 'speedRight':speedRight};
    console.log('drive start');
    self.postMessage({"message":"serverCall", "msg":JSON.stringify(msg)})
    console.log('drive end');
}


function robot_get_list_of_marker_ids() {
    if(lastMarkers==null) return [];
    var markerIds=[];
    for(i=0;i<lastMarkers.length;i++) {
        markerIds.push(lastMarkers[i].id);
    }
    return markerIds;
}

function robot_get_distance_to_marker(markerId) {
    if(lastMarkers==null) return 0;
    for(i=0;i<lastMarkers.length;i++) {
        if(lastMarkers[i].id==markerId){
            return lastMarkers[i]['distance'];
        }
    }
    return 0;
}

function robot_get_x_angle_to_marker(markerId) {
    if(lastMarkers==null) return 0;
    for(i=0;i<lastMarkers.length;i++) {
        if(lastMarkers[i].id==markerId){
            return lastMarkers[i]['xAngle'];
        }
    }
    return 0;
}

function robot_get_y_angle_to_marker(markerId) {
    if(lastMarkers==null) return 0;
    for(i=0;i<lastMarkers.length;i++) {
        if(lastMarkers[i].id==markerId){
            return lastMarkers[i]['yAngle'];
        }
    }
    return 0;
}

function robot_say_text(text, lang){
    var msg = {"command": 'say', 'text': text, 'lang':lang};
    console.log('say text');
    self.postMessage({"message":"serverCall", "msg":JSON.stringify(msg)})
}

function robot_display_text(text, lines){
    var msg = {"command": 'display_text', 'text': text, 'lines': lines};
    console.log('display text');
    self.postMessage({"message":"serverCall", "msg":JSON.stringify(msg)})
}

function robot_display_clear(lines){
    var msg = {"command": 'display_clear', 'lines': lines};
    console.log('display clear');
    self.postMessage({"message":"serverCall", "msg":JSON.stringify(msg)})
}

function robot_stop() {
    console.log('stop robot: start');
    lastDriveParams = {'speedLeft':0, 'speedRight':0}
    self.postMessage({"message":"serverCall", "msg":JSON.stringify({"command": 'drive', 'speedLeft': 0, 'speedRight':0})});
    console.log('stop robot: end');
}

