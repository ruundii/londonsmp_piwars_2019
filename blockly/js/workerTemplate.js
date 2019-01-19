var window = new WindowStub();
var running = false;
var lastAliens = null;

var lastDriveParams = null;

function WindowStub(){

}

WindowStub.prototype.alert = function(msg){
    self.postMessage({"message":"alert", "msg":msg});
}

self.onmessage = function(e) {
   if(e.data=='start'){
       runBlocklyCode();
   }
   else if(e.data.message=='updateAlienReadings'){
       lastAliens = e.data['aliens'];
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


function robot_stop() {
    console.log('stop robot: start');
    lastDriveParams = {'speedLeft':0, 'speedRight':0}
    self.postMessage({"message":"serverCall", "msg":JSON.stringify({"command": 'drive', 'speedLeft': 0, 'speedRight':0})});
    console.log('stop robot: end');
}

function robot_get_list_of_alien_ids() {
    if(lastAliens==null) return [];
    var alienIds=[];
    for(i=0; i<lastAliens.length; i++) {
        alienIds.push(lastAliens[i].id);
    }
    return alienIds;
}

function robot_get_distance_to_alien(alienId) {
    if(lastAliens==null) return 0;
    for(i=0; i<lastAliens.length; i++) {
        if(lastAliens[i].id==alienId){
            return lastAliens[i]['distance'];
        }
    }
    return 0;
}

function robot_get_x_angle_to_alien(alienId) {
    if(lastAliens==null) return 0;
    for(i=0; i<lastAliens.length; i++) {
        if(lastAliens[i].id==alienId){
            return lastAliens[i]['xAngle'];
        }
    }
    return 0;
}

function robot_get_y_angle_to_alien(alienId) {
    if(lastAliens==null) return 0;
    for(i=0; i<lastAliens.length; i++) {
        if(lastAliens[i].id==alienId){
            return lastAliens[i]['yAngle'];
        }
    }
    return 0;
}

function robot_set_camera_mode(mode){
    var msg = {"command": 'setCameraMode', 'mode': mode};
    console.log('robot_set_camera_mode');
    self.postMessage({"message":"serverCall", "msg":JSON.stringify(msg)})
}


