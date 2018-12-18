'use strict';

goog.provide('Blockly.Python.Robot');

goog.require('Blockly.Python');


Blockly.Python['robot_drive'] = function(block) {
    var speedLeft = Blockly.Python.valueToCode( block, 'robot_motor_speed_left', Blockly.Python.ORDER_NONE) || '0';
    var speedRight = Blockly.Python.valueToCode( block, 'robot_motor_speed_right', Blockly.Python.ORDER_NONE) || '0';
    var code = "robot_drive("+speedLeft+","+speedRight+")\n";
    return code;
};

Blockly.Python['robot_get_list_of_marker_ids'] = function(block) {
    var code = "robot_get_list_of_marker_ids()";
    return [code, Blockly.Python.ORDER_FUNCTION_CALL];
};

Blockly.Python['robot_get_distance_to_marker'] = function(block) {
    var markerId = Blockly.Python.valueToCode( block, 'marker_id', Blockly.Python.ORDER_NONE) || '0';
    var code = "robot_get_distance_to_marker("+markerId+")";
    return [code, Blockly.Python.ORDER_FUNCTION_CALL];
};

Blockly.Python['robot_get_x_angle_to_marker'] = function(block) {
    var markerId = Blockly.Python.valueToCode( block, 'marker_id', Blockly.Python.ORDER_NONE) || '0';
    var code = "robot_get_x_angle_to_marker("+markerId+")";
    return [code, Blockly.Python.ORDER_FUNCTION_CALL];
};

Blockly.Python['robot_get_y_angle_to_marker'] = function(block) {
    var markerId = Blockly.Python.valueToCode( block, 'marker_id', Blockly.Python.ORDER_NONE) || '0';
    var code = "robot_get_y_angle_to_marker("+markerId+")";
    return [code, Blockly.Python.ORDER_FUNCTION_CALL];
};

Blockly.Python['robot_say_text'] = function(block) {
    var msg = Blockly.Python.valueToCode(block, 'text',
        Blockly.Python.ORDER_NONE) || '\'\'';
    var lang = block.getFieldValue('lang');
    var code = "robot_say_text("+msg+", '"+lang+"')\n";
    return code;
};

Blockly.Python['robot_display_text'] = function(block) {
    var line = block.getFieldValue('line');
    var msg = Blockly.Python.valueToCode(block, 'text',
        Blockly.Python.ORDER_NONE) || '\'\'';
    var code = "robot_display_text("+msg+", "+line+")\n";
    return code;
};

Blockly.Python['robot_display_clear'] = function(block) {
    var line = block.getFieldValue('line');
    var code = "robot_display_clear("+line+")\n";
    return code;
};

Blockly.Python['robot_stop'] = function(block) {
    var code = "robot_stop()\n";
    return code;
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