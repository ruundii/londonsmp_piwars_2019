var mapVisualiser = new MapVisualiser();
var svg;

var imgChassis;
var imgChassisEstimate;
var sceneWidth = 800;
var sceneHeight=600;
var degreesInRadians = 180 / Math.PI;

var currentCoordinates = {
    x:200,
    y:200,
    theta: 0
}

var currentEstimatedCoordinates = {
    x:200,
    y:200,
    theta: 0
}

var currentReadings = null;

var sensorConfiguration = {
    FL:{
        relTheta: 45,
        positionDistance: 13.04,
        positionTheta: 32.47, //arctan(7/11)*180/pi
        angleRange:15,
        minDistance:2,
        maxDistance:150
    },
    FC:{
        relTheta: 0,
        positionDistance: 14,
        positionTheta: 0,
        angleRange:15,
        minDistance:2,
        maxDistance:150
    },
    FR:{
        relTheta: -45,
        positionDistance: 13.04,
        positionTheta: -32.47,
        angleRange:15,
        minDistance:2,
        maxDistance:150
    },
    ML:{
        relTheta: 90,
        positionDistance: 9,
        positionTheta: 90,
        angleRange:15,
        minDistance:3,
        maxDistance:39
    },
    MR:{
        relTheta: -90,
        positionDistance: 9,
        positionTheta: -90,
        angleRange:15,
        minDistance:3,
        maxDistance:39
    },
    BL:{
        relTheta: 135,
        positionDistance: 13.04,
        positionTheta: 147.53,
        angleRange:15,
        minDistance:9,
        maxDistance:80
    },
    BC:{
        relX : -13,
        relY: 0,
        relTheta: 180,
        positionDistance: 13,
        positionTheta: 180,
        angleRange:15,
        minDistance:2,
        maxDistance:150
    },
    BR:{
        relTheta: -135,
        positionDistance: 13.04,
        positionTheta: -147.53,
        angleRange:15,
        minDistance:9,
        maxDistance:80
    }
};

var currentSensorPaths = []

function MapVisualiser(){

}

MapVisualiser.prototype.showVisualisation = async function(){
    if(svg!=null){
        svg.remove();
    }
    svg = SVG('divMap').size(sceneWidth, sceneHeight);
    svg.viewbox(0,0,500,400);
    var loadSVG = new XMLHttpRequest;
    loadSVG.onload = function(){
        svg = svg.svg(loadSVG.responseText);
        imgChassis = svg.image('media/chassis.svg').size(22, 27).opacity(0.9).hide();
        if(isSimulation) {
            imgChassisEstimate = svg.image('media/chassis.svg').size(22, 27).opacity(0.6).hide();
        }
        $('#divMap').show();
    };
    loadSVG.open("GET", '/svgs/living-room.svg', true);
    loadSVG.send();

}

MapVisualiser.prototype.stopVisualisation = function(){
    $('#divMap').hide();
}

MapVisualiser.prototype.setRobotCoordinates = function(isEstimate, x, y, theta) {
    if(svg==null || imgChassis==null) return;
    if(!isSimulation || (isSimulation&&!isEstimate)){
        currentCoordinates = {x:x, y:y, theta:theta};
        imgChassis.show();
        imgChassis.rotate(0);
        var translatedCoords = getTranslatedCoords(currentCoordinates);
        imgChassis.center(translatedCoords.x,translatedCoords.y);
        imgChassis.rotate(-theta+90);

    }
    else{
        currentEstimatedCoordinates = {x:x, y:y, theta:theta};
        imgChassisEstimate.rotate(0);
        imgChassisEstimate.show();
        var translatedCoords = getTranslatedCoords(currentEstimatedCoordinates);
        imgChassisEstimate.center(translatedCoords.x,translatedCoords.y);
        imgChassisEstimate.rotate(-theta+90);
    }
    mapVisualiser.drawSensors();
}

MapVisualiser.prototype.drawSensors = function() {
    for(var i=0; i< currentSensorPaths.length;i++){
        currentSensorPaths[i].remove();
    }
    currentSensorPaths = [];
    mapVisualiser.drawSensor(sensorConfiguration.FL, currentReadings == null ? null : currentReadings.FL);
    mapVisualiser.drawSensor(sensorConfiguration.FC, currentReadings == null ? null : currentReadings.FC);
    mapVisualiser.drawSensor(sensorConfiguration.FR, currentReadings == null ? null : currentReadings.FR);
    mapVisualiser.drawSensor(sensorConfiguration.ML, currentReadings == null ? null : currentReadings.ML);
    mapVisualiser.drawSensor(sensorConfiguration.MR, currentReadings == null ? null : currentReadings.MR);
    mapVisualiser.drawSensor(sensorConfiguration.BL, currentReadings == null ? null : currentReadings.BL);
    mapVisualiser.drawSensor(sensorConfiguration.BC, currentReadings == null ? null : currentReadings.BC);
    mapVisualiser.drawSensor(sensorConfiguration.BR, currentReadings == null ? null : currentReadings.BR);
}

MapVisualiser.prototype.drawSensor = function(sensorConfig, sensorReading) {
    if(svg==null) return;

    var sensorCoords = {
        x:currentCoordinates.x + sensorConfig.positionDistance*cos(currentCoordinates.theta+sensorConfig.positionTheta),
        y:currentCoordinates.y + sensorConfig.positionDistance*sin(currentCoordinates.theta+sensorConfig.positionTheta),
        theta:currentCoordinates.theta + sensorConfig.relTheta
    }
    var startAngle = sensorCoords.theta + sensorConfig.angleRange/2;
    var startArcCoord = {
        x: sensorCoords.x + sensorConfig.maxDistance*cos(startAngle),
        y: sensorCoords.y + sensorConfig.maxDistance*sin(startAngle)
    }

    var endAngle = sensorCoords.theta - sensorConfig.angleRange/2;
    var endArcCoord = {
        x: sensorCoords.x + sensorConfig.maxDistance*cos(endAngle),
        y: sensorCoords.y + sensorConfig.maxDistance*sin(endAngle)
    }

    var sensorCoordsTran = getTranslatedCoords(sensorCoords);
    var startArcCoordTran = getTranslatedCoords(startArcCoord);
    var endArcCoordTran = getTranslatedCoords(endArcCoord);

    currentSensorPaths.push(
        svg.path("M "+sensorCoordsTran.x+" "+sensorCoordsTran.y+" L "+startArcCoordTran.x+" "+startArcCoordTran.y +
            " A "+ sensorConfig.maxDistance +" " + sensorConfig.maxDistance+ " 0 0 1 "+endArcCoordTran.x+" "+endArcCoordTran.y+
            "z").attr({fill: '#acf', 'stroke-width':'1', stroke:'#000','stroke-opacity':'0.5'}).opacity(0.4));
    if(sensorReading!=null){
        var readingStartArcCoordTran = getTranslatedCoords({
            x: sensorCoords.x + sensorReading*cos(startAngle),
            y: sensorCoords.y + sensorReading*sin(startAngle)
        });
        var readingEndArcCoordTran = getTranslatedCoords({
            x: sensorCoords.x + sensorReading*cos(endAngle),
            y: sensorCoords.y + sensorReading*sin(endAngle)
        });

        currentSensorPaths.push(
            svg.path("M "+readingStartArcCoordTran.x+" "+readingStartArcCoordTran.y+
                " A "+ sensorReading +" " + sensorReading+ " 0 0 1 "+readingEndArcCoordTran.x+" "+readingEndArcCoordTran.y+
                "z").attr({fill: 'none', 'stroke-width':'1', stroke:'red','stroke-opacity':'0.5'}));
    }

}

MapVisualiser.prototype.updateSensorReadings = function(readings){
    currentReadings = readings;
    mapVisualiser.drawSensors();
}


MapVisualiser.prototype.sleep = function(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getTranslatedCoords(coords){
    return {x: coords.x, y: 400-coords.y};
}

function cos(degrees){
    return Math.cos(degrees/degreesInRadians);
}

function sin(degrees){
    return Math.sin(degrees/degreesInRadians);
}
