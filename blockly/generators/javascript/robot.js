'use strict';

goog.provide('Blockly.JavaScript.Robot');

goog.require('Blockly.JavaScript');


Blockly.JavaScript['robot_drive'] = function(block) {
    var speed_left = Blockly.JavaScript.valueToCode( block, 'robot_motor_speed_left', Blockly.JavaScript.ORDER_NONE) || '0';
    var speed_right = Blockly.JavaScript.valueToCode( block, 'robot_motor_speed_right', Blockly.JavaScript.ORDER_NONE) || '0';
    var code = "robot_drive("+speed_left+","+speed_right+");\n";
    return code;
};


Blockly.JavaScript['robot_stop'] = function(block) {
    var code = "robot_stop();\n";
    return code;
};

Blockly.JavaScript['robot_set_camera_mode'] = function(block) {
    var mode = block.getFieldValue('mode');
    var code = "robot_set_camera_mode("+mode+");\n";
    return code;
};

Blockly.JavaScript['robot_get_list_of_alien_ids'] = function(block) {
    var code = "robot_get_list_of_alien_ids()";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_distance_to_alien'] = function(block) {
    var alien_id = Blockly.JavaScript.valueToCode( block, 'alien_id', Blockly.JavaScript.ORDER_NONE) || '0';
    var code = "robot_get_distance_to_alien("+alien_id+")";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_x_angle_to_alien'] = function(block) {
    var alien_id = Blockly.JavaScript.valueToCode( block, 'alien_id', Blockly.JavaScript.ORDER_NONE) || '0';
    var code = "robot_get_x_angle_to_alien("+alien_id+")";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_y_angle_to_alien'] = function(block) {
    var alien_id = Blockly.JavaScript.valueToCode( block, 'alien_id', Blockly.JavaScript.ORDER_NONE) || '0';
    var code = "robot_get_y_angle_to_alien("+alien_id+")";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_list_of_coloured_sheets'] = function(block) {
    var code = "robot_get_list_of_coloured_sheets()";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_distance_to_a_coloured_sheet'] = function(block) {
    var colour = block.getFieldValue('colour');
    var code = "robot_get_distance_to_a_coloured_sheet('"+colour+"')";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.JavaScript['robot_get_x_angle_to_a_coloured_sheet'] = function(block) {
    var colour = block.getFieldValue('colour');
    var code = "robot_get_x_angle_to_a_coloured_sheet('"+colour+"')";
    return [code, Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

function escape (val) {
    return val
        .replace(/[\\]/g, '\\\\')
        .replace(/[\/]/g, '\\/')
        .replace(/[\b]/g, '\\b')
        .replace(/[\f]/g, '\\f')
        .replace(/[\n]/g, '\\n')
        .replace(/[\r]/g, '\\r')
        .replace(/[\t]/g, '\\t')
        .replace(/[\"]/g, '\\"')
        .replace(/\\'/g, "\\'");
}
