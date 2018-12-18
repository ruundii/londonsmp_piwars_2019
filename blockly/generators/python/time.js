'use strict';

goog.provide('Blockly.Python.time');

goog.require('Blockly.Python');


Blockly.Python['time_wait_milliseconds'] = function(block) {
    Blockly.Python.definitions_['import_time'] = 'import time';
    var delayTime = Blockly.Python.valueToCode( block, 'ms', Blockly.Python.ORDER_NONE) || '0';
    var code = 'time.sleep(' + delayTime + ')\n';
    return code;

};
