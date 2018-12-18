'use strict';

goog.provide('Blockly.JavaScript.time');

goog.require('Blockly.JavaScript');


Blockly.JavaScript['time_wait_milliseconds'] = function(block) {
    // Blockly.JavaScript.definitions_['sleep_milliseconds'] = 'function sleepMilliseconds(ms) {\n' +
    //         '  // sleep ms milliseconds\n' +
    //         '  var start = new Date().getTime();\n' +
    //         '  for (var i = 0; i < 1e7; i++) {\n' +
    //         '    if ((new Date().getTime() - start) > ms){\n' +
    //         '      break;\n' +
    //         '    }\n' +
    //         '  }\n' +
    //         '}';
    var delayTime = Blockly.JavaScript.valueToCode( block, 'ms', Blockly.JavaScript.ORDER_NONE) || '0';
    var code = 'await sleep(' + delayTime + ');\n';
    return code;

};
