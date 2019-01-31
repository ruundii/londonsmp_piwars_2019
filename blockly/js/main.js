var piwarsRobot = new PiWarsRobot();
var workspace = null;
var files = null;
var showMap = true;

function PiWarsRobot() {
}

PiWarsRobot.prototype.initPiWarsRobot = function () {
    if (localStorage.showMap != null) showMap = localStorage.showMap == 'true';
    piwarsRobot.initBlockly();
    codeEditor.initCodeEditor();
    piwarsRobot.initialisePageComponents();
    codeRunner.initCodeRunner();
    webSocketManager.initWebSocketManager();
    if (localStorage.piwarsBlockly != null) {
        try {
            var xml = Blockly.Xml.textToDom(localStorage.piwarsBlockly);
        } catch (e) {
            piwarsRobot.displayMessage('Error parsing XML:\n' + e, 'error');
            return;
        }
        workspace.clear();
        Blockly.Xml.domToWorkspace(xml, workspace);
        piwarsRobot.renderContent()
    }
}

PiWarsRobot.prototype.displayMessage = function (msg, type) {
    try {

        switch (type) {
            case 'error':
                M.toast({html: msg, displayLength: 5000, classes: "red"});
                break;
            case 'system':
                M.toast({html: msg, displayLength: 5000, classes: "yellow darken-3"});
                break;
            default:
                M.toast({html: msg, displayLength: 5000});
                break;
        }
    }
    catch (exc) {
        console.log("Display message issue:" + exc);
    }
}


PiWarsRobot.prototype.initBlockly = function () {
    Blockly.HSV_SATURATION = 0.6;
    Blockly.HSV_VALUE = 0.7;
    files = null;
    workspace = Blockly.inject(document.getElementById('blocklyDiv'),
        {
            toolbox: document.getElementById('toolbox'),
            media: 'media/',
            zoom: {
                controls: true,
                wheel: false,
                startScale: 1.0,
                maxScale: 2,
                minScale: 0.2,
                scaleSpeed: 1.2
            },
            grid:
                {
                    spacing: 30,
                    length: 3,
                    colour: '#eee',
                    snap: true
                }
        });
    piwarsRobot.bindBlocklyEventListeners();
}

PiWarsRobot.prototype.renderContent = function () {
    workspace.render();
    codeEditor.render();
    localStorage.piwarsBlockly = piwarsRobot.generateXml();
}

PiWarsRobot.prototype.bindBlocklyEventListeners = function () {
    workspace.addChangeListener(function (event) {
        if (event.type != Blockly.Events.UI) {
            piwarsRobot.renderContent();
        }
        else {
            localStorage.piwarsBlockly = piwarsRobot.generateXml();
        }
    });
};

PiWarsRobot.prototype.initialisePageComponents = function () {
    $('#fileNameToSave').on('keyup', piwarsRobot.updateSelectedFileRowEvent);
    $('#fileNameToSave').on('change', piwarsRobot.updateSelectedFileRowEvent);
    $('#fileNameToSave').on('blur', piwarsRobot.updateSelectedFileRowEvent);
    $('.modal').modal({
        onOpenStart: function () {
            piwarsRobot.initialiseFileDialogOnOpen();
        }
    });
    $(".dropdown-trigger").dropdown();
    $('#openLoadProjectDialogButton').on('click', piwarsRobot.initLoadProjectDialog);
    $('#openSaveProjectDialogButton').on('click', piwarsRobot.initSaveProjectDialog);
    $('#newProjectButton').on('click', piwarsRobot.startNewProject);
    $('#runButton').on('click', codeRunner.runCodeButtonHandler);
    $('#runOnRobotButton').on('click', codeRunner.runOnRobotButtonHandler);
    $('#driveButton').on('click', piwarsRobot.driveRobot);
    $('#stopButton').on('click', codeRunner.stopCodeButtonHandler);

    $('#selectLanguagePython').on('click', piwarsRobot.selectLanguagePython);
    $('#selectLanguageJavascript').on('click', piwarsRobot.selectLanguageJavascript);
    $('#selectLanguageXML').on('click', piwarsRobot.selectLanguageXML);
    $('#mapButton').on('click', piwarsRobot.toggleMapButton);
    $('#btnCloseDriveControls').on('click', piwarsRobot.closeDriveControls);
    $('#mapButtonIcon')[0].innerHTML = showMap ? 'check' : 'clear';

    var sliderLeft = document.getElementById('drive-slider-left');
    noUiSlider.create(sliderLeft, {
        start: [0],
        connect: false,
        step: 5,
        direction: 'rtl',
        behaviour: 'snap',
        orientation: 'vertical', // 'horizontal' or 'vertical'
        range: {
            'min': -100,
            'max': 100
        },
        format: wNumb({
		decimals: 0
	    })
    });

    var sliderRight = document.getElementById('drive-slider-right');
    noUiSlider.create(sliderRight, {
        start: [0],
        connect: false,
        step: 5,
        direction: 'rtl',
        behaviour: 'snap',
        orientation: 'vertical', // 'horizontal' or 'vertical'
        range: {
            'min': -100,
            'max': 100
        },
        format: wNumb({
		decimals: 0
	    })
    });
    $('#mapButton').hide();
    $('#driveButton').hide();
    $('#simulateButton').hide();
}

PiWarsRobot.prototype.startNewProject = function () {
    if (confirm("Starting new project will drop all unsaved work. Ok?")) {
        localStorage.piwarsBlockly = null;
        workspace.clear();
    }
}

PiWarsRobot.prototype.driveRobot = function () {
    var sliderLeft = document.getElementById('drive-slider-left');
    var sliderRight = document.getElementById('drive-slider-right');

    sliderLeft.noUiSlider.on('update', function (values) {
        webSocketManager.sendMessage(JSON.stringify({"command": 'drive', 'speedLeft': sliderLeft.noUiSlider.get(), 'speedRight':sliderRight.noUiSlider.get()}));
    });

    sliderLeft.noUiSlider.on('end', function () {
        sliderLeft.noUiSlider.set(0);
        webSocketManager.sendMessage(JSON.stringify({"command": 'drive', 'speedLeft': sliderLeft.noUiSlider.get(), 'speedRight':sliderRight.noUiSlider.get()}));
    });

    sliderRight.noUiSlider.on('update', function (values) {
        webSocketManager.sendMessage(JSON.stringify({"command": 'drive', 'speedLeft': sliderLeft.noUiSlider.get(), 'speedRight':sliderRight.noUiSlider.get()}));
    });

    sliderRight.noUiSlider.on('end', function () {
        sliderRight.noUiSlider.set(0);
        webSocketManager.sendMessage(JSON.stringify({"command": 'drive', 'speedLeft': sliderLeft.noUiSlider.get(), 'speedRight':sliderRight.noUiSlider.get()}));
    });

    $('#divDriveControls').show();
}

PiWarsRobot.prototype.closeDriveControls = function () {
    var sliderLeft = document.getElementById('drive-slider-left');
    var sliderRight = document.getElementById('drive-slider-right');
    sliderLeft.noUiSlider.off();
    sliderRight.noUiSlider.off();
    $('#divDriveControls').hide();
}

PiWarsRobot.prototype.toggleMapButton = function () {
    showMap = !showMap;
    localStorage.showMap = showMap;
    $('#mapButtonIcon')[0].innerHTML = showMap ? 'check' : 'clear';

}

PiWarsRobot.prototype.selectLanguagePython = function () {
    $(".dropdown-trigger")[0].innerHTML = $(".dropdown-trigger")[0].innerHTML.replace("Javascript", "Python").replace("XML", "Python");
    codeEditor.setLanguage("Python");
}

PiWarsRobot.prototype.selectLanguageJavascript = function () {
    $(".dropdown-trigger")[0].innerHTML = $(".dropdown-trigger")[0].innerHTML.replace("Python", "Javascript").replace("XML", "Javascript");
    codeEditor.setLanguage("Javascript");
}

PiWarsRobot.prototype.selectLanguageXML = function () {
    $(".dropdown-trigger")[0].innerHTML = $(".dropdown-trigger")[0].innerHTML.replace("Python", "XML").replace("Javascript", "XML");
    codeEditor.setLanguage("XML");
}

PiWarsRobot.prototype.initLoadProjectDialog = function () {
    $('#fileNameToSaveRow').hide();
    $('#loadFileButton').show();
    $('#saveFileButton').hide();
    piwarsRobot.setLoadProjectButtonState();
}

PiWarsRobot.prototype.setLoadProjectButtonState = function () {
    var selectedItem = $('input[type=radio][name=rbtnFileSelected]:checked');
    if (selectedItem != null && selectedItem.length > 0) {
        $('#loadFileButton').prop('disabled', false).removeClass('disabled').on("click");
        $('#loadFileButton').off('click', piwarsRobot.loadFile);
        $('#loadFileButton').on('click', piwarsRobot.loadFile);
    }
    else {
        $('#loadFileButton').prop('disabled', true).addClass('disabled').off("click");
    }
}

PiWarsRobot.prototype.initSaveProjectDialog = function () {
    $('#fileNameToSaveRow').show();
    $('#loadFileButton').hide();
    $('#saveFileButton').show();
}

PiWarsRobot.prototype.initialiseFileDialogOnOpen = function () {
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: 'http://' + location.hostname + ':8000/files/',
        timeout: 5000,
        //async: false,
        success: function (response) {
            var trHTML = '';
            files = response.files;
            $.each(response.files, function (i, item) {
                trHTML += '<tr><td>' + item.name + '</td><td>' + item.lastModifiedDate + '</td><td><label><input class="with-gap" id="rbtnFileSelected' + i + '" value="' + i + '" name="rbtnFileSelected" type="radio"/><span></span></label></td></tr>';
            });
            $('#filesList').html(trHTML);
            $('input[type=radio][name=rbtnFileSelected]').on('change', function (data) {
                $('#fileNameToSave').val(response.files[$(this).val()].name);
                piwarsRobot.updateSelectedFileRowEvent();
                piwarsRobot.setLoadProjectButtonState();
            });
            piwarsRobot.updateSelectedFileRow();
        },
        error: function (xhr, textStatus, errorThrown) {
            piwarsRobot.displayMessage('Files request failed.' + errorThrown, 'error');
        }
    });
    piwarsRobot.validateFileName(true);
}

PiWarsRobot.prototype.updateSelectedFileRowEvent = function () {
    piwarsRobot.updateSelectedFileRow();
    piwarsRobot.validateFileName(false);
}

PiWarsRobot.prototype.updateSelectedFileRow = function () {
    if (files != null && files.length > 0) {
        $.each(files, function (i, item) {

            if (item.name.toLowerCase() == $('#fileNameToSave').val().toString().toLowerCase()) {
                $('#rbtnFileSelected' + i).prop("checked", true);
            }
            else {
                $('#rbtnFileSelected' + i).prop("checked", false);
            }
        });
    }
}

PiWarsRobot.prototype.validateFileName = function (initial) {
    if (!initial) M.validate_field($('#fileNameToSave'));

    if ($('#fileNameToSave')[0].checkValidity()) {
        $('#saveFileButton').prop('disabled', false).removeClass('disabled').on("click");
        $('#saveFileButton').off('click', piwarsRobot.saveFile);
        $('#saveFileButton').on('click', piwarsRobot.saveFile);
    }
    else {
        $('#saveFileButton').prop('disabled', true).addClass('disabled').off("click");
    }
}


PiWarsRobot.prototype.saveFile = function () {
    if (!$('#fileNameToSave')[0].checkValidity()) {
        $('#fileNameToSave')[0].reportValidity();
        return;
    }
    var fileName = $('#fileNameToSave').val().toString();
    var formData = new FormData();
    formData.append("fileName", fileName);
    formData.append("fileContent", piwarsRobot.generateXml());
    $.ajax({
        url: "http://" + location.hostname + ":8000/files/upload",
        data: formData,
        type: 'POST',
        dataType: 'json',
        cache: false,
        contentType: false,
        processData: false,
        success: function (data, textStatus, jqXHR) {
            piwarsRobot.displayMessage('Saved');
        },
        error: function (jqXHR, textStatus, errorThrown) {
            piwarsRobot.displayMessage('Failed to save.' + errorThrown, 'error');
        }
    });

}

PiWarsRobot.prototype.generateXml = function () {
    var xmlDom = Blockly.Xml.workspaceToDom(workspace);
    return Blockly.Xml.domToPrettyText(xmlDom);
}

PiWarsRobot.prototype.loadFile = function () {
    var selectedItem = $('input[type=radio][name=rbtnFileSelected]:checked');
    if (selectedItem == null || selectedItem.length < 1) return;
    $.ajax({
        type: 'GET',
        dataType: 'text',
        url: 'http://' + location.hostname + ':8000/files/' + encodeURI(files[selectedItem[0].value].name),
        timeout: 5000,
        cache: false,
        async: false,
        success: function (response) {
            try {
                var xml = Blockly.Xml.textToDom(response);
            } catch (e) {
                piwarsRobot.displayMessage('Error parsing XML:\n' + e, 'error');
                return;
            }
            workspace.clear();
            Blockly.Xml.domToWorkspace(xml, workspace);
        },
        error: function (xhr, textStatus, errorThrown) {
            piwarsRobot.displayMessage('Files request failed.' + errorThrown, 'error');
        }
    });
}


