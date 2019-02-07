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


Blockly.Blocks['robot_set_camera_mode'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_set_camera_mode",
                "message0": "Set camera mode  %1",
                "args0": [
                    {"type":"field_dropdown",
                        "name":"mode",
                        "options":[["Detect aliens","0"],["Detect colored sheets","1"],["Detect white line track","2"], ["Off","-1"]]},
                ],
                "inputsInline": true,
                "previousStatement": null,
                "nextStatement": null,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Set camera mode according to a challenge",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_list_of_alien_ids'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_list_of_alien_ids",
                "message0": "Get list of visible aliens",
                "inputsInline": true,
                "output": "Array",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get list of ids of currently visible aliens",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_distance_to_alien'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_distance_to_alien",
                "message0": "Get distance to alien with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "alien_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get distance to alien with id in cm",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_x_angle_to_alien'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_x_angle_to_alien",
                "message0": "Get x angle to alien with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "alien_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get x angle to alien with id in degrees",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_y_angle_to_alien'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_y_angle_to_alien",
                "message0": "Get y angle to alien with id %1",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "alien_id",
                        "check": "Number"
                    }
                ],
                "inputsInline": true,
                "output": "Number",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get y angle to alien with id in degrees",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_list_of_coloured_sheets'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_list_of_coloured_sheets",
                "message0": "Get list of visible coloured sheets",
                "inputsInline": true,
                "output": "Array",
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get list of currently visible coloured sheets",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_distance_to_a_coloured_sheet'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_distance_to_a_coloured_sheet",
                "message0": "Get distance to a sheet painted in %1",
                "args0": [
                    {"type":"field_dropdown",
                        "name":"colour",
                        "options":[["green","green"],["blue","blue"],["red","red"], ["yellow","yellow"]]},
                ],
                "output": "Number",
                "inputsInline": true,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get distance to a coloured sheet in cm",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_x_angle_to_a_coloured_sheet'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_x_angle_to_a_coloured_sheet",
                "message0": "Get x angle to a sheet painted in %1",
                "args0": [
                    {"type":"field_dropdown",
                        "name":"colour",
                         "options":[["green","green"],["blue","blue"],["red","red"], ["yellow","yellow"]]},
                ],
                "output": "Number",
                "inputsInline": true,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get x angle to a coloured sheet in degrees",
                "helpUrl": ""
            });
    }
};

Blockly.Blocks['robot_get_x_angle_to_a_white_line'] = {
    init: function () {
        this.jsonInit(
            {
                "type": "robot_get_x_angle_to_a_white_line",
                "message0": "Get x angle to a white line %1 crossing line",
                "args0": [
                    {"type":"field_dropdown",
                        "name":"cross_line_number",
                         "options":[["near","1"],["far","2"]]},
                ],
                "output": "Number",
                "inputsInline": true,
                "colour": Blockly.Blocks.Robot.HUE,
                "tooltip": "Get x angle to a white line intersection with a cross line",
                "helpUrl": ""
            });
    }
};
