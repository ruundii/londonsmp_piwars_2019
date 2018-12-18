'use strict';

goog.provide('Blockly.Blocks.Robot');
goog.require('Blockly.Blocks');

Blockly.Blocks.Robot.HUE = 0;

Blockly.Blocks['robot_drive'] = {
    init: function () {
        this.jsonInit({
            "message0":"Drive with speed left: %1 right: %2",
            "args0":[
                {
                    "type": "input_value",
                    "name": "robot_motor_speed_left",
                    "check": "Number"
                },
                {
                    "type": "input_value",
                    "name": "robot_motor_speed_right",
                    "check": "Number"
                }
                ],
            "inputsInline":true,
            "previousStatement":null,
            "nextStatement":null,
            "colour": Blockly.Blocks.Robot.HUE,
            "tooltip":"Speed should be in a range from -100 to 100",
            "helpUrl":""

        });
    }
};


Blockly.Blocks['robot_stop'] = {
    init: function () {
        this.jsonInit({
            "message0":"Stop robot",
            "previousStatement":null,
            "nextStatement":null,
            "colour": Blockly.Blocks.Robot.HUE,
            "tooltip":"",
            "helpUrl":""
        });
    }
};



Blockly.Blocks['robot_get_list_of_marker_ids'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_list_of_marker_ids",
                "message0": "Get list of visible marker ids",
                "inputsInline": true,
                "output": "Array",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get list of ids of currently visible markers",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_distance_to_marker'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_distance_to_marker",
                "message0": "Get distance to marker with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "marker_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get distance to marker with id in cm",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_x_angle_to_marker'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_x_angle_to_marker",
                "message0": "Get x angle to marker with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "marker_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get x angle to marker with id in degrees",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_y_angle_to_marker'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_y_angle_to_marker",
                "message0": "Get y angle to marker with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "marker_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get y angle to marker with id in degrees",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_say_text'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_say_text",
                "message0": "Say %1 in %2",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "text",
                    },
                    {"type":"field_dropdown",
                        "name":"lang",
                        "options":[["English (UK)","en-gb"],["English (US)","en-us"],["Russian","ru"]]}
                ],
                "inputsInline": true,
                "previousStatement": null,
                "nextStatement": null,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Pronounce the specified text",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_display_text'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_display_text",
                "message0": "Display %1 in line %2",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "text",
                    },
                    {"type":"field_dropdown",
                        "name":"line",
                        "options":[["1","1"],["2","2"]]},
                ],
                "inputsInline": true,
                "previousStatement": null,
                "nextStatement": null,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Display the specified text (up to 16 characters) in a specified line of the display",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_display_clear'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_display_clear",
                "message0": "Clear display line(s) %1",
                "args0": [
                    {"type":"field_dropdown",
                        "name":"line",
                        "options":[["1 and 2","0"],["1","1"],["2","2"]]},
                ],
                "inputsInline": true,
                "previousStatement": null,
                "nextStatement": null,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Clear specified lines of the display",
                "helpUrl": ""
            });
    }
};