'use strict';

goog.provide('Blockly.Blocks.Mytime');
goog.require('Blockly.Blocks');

Blockly.Blocks.Mytime.HUE = 140;

Blockly.Blocks['time_wait_milliseconds'] = {
    init: function() {
        this.jsonInit({
            "message0": "wait %1 milliseconds",
            "args0": [
                {
                    "type": "input_value",
                    "name": "ms",
                    "check": "Number"
                }
            ],
            "inputsInline": true,
            "previousStatement": null,
            "nextStatement": null,
            "colour": Blockly.Blocks.Mytime.HUE
        });
    }
};
