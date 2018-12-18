svgEditor.addExtension("robot_file_save", {
    callback: function() {
        'use strict';
        var fileDialog;
        var files;
        var svgData;

        function updateSelectedFileRowEvent (){
            updateSelectedFileRow();
            validateFileName(false);
        }

        function updateSelectedFileRow (){
            if (files != null && files.length > 0) {
                $.each(files, function (i, item) {

                    if (item.name.toLowerCase() == $('#fileNameToSave').val().toString().toLowerCase()) {
                        $('#rbtnFileSelected' + i).prop("checked", true);
                    }
                    else{
                        $('#rbtnFileSelected' + i).prop("checked", false);
                    }
                });
            }
        }

        function validateFileName(initial){
            if($('#fileNameToSave')[0].checkValidity()){
                $('.ui-dialog-buttonpane').find('button:nth-child(2)').button( "option", "disabled", false);
            }
            else{
                $('.ui-dialog-buttonpane').find('button:nth-child(2)').button( "option", "disabled", true);
            }
        }

        function setLoadButtonState() {
            var selectedItem = $('input[type=radio][name=rbtnFileSelected]:checked');
            if(selectedItem!= null && selectedItem.length>0) {
                $('.ui-dialog-buttonpane').find('button:nth-child(1)').button( "option", "disabled", false);

            }
            else{
                $('.ui-dialog-buttonpane').find('button:nth-child(1)').button( "option", "disabled", true);
            }
        }

        function loadFilesList(){
            $.ajax({
                type: 'GET',
                dataType: 'json',
                url: 'http://'+location.hostname+':8000/svgs/',
                timeout: 5000,
                async: false,
                success: function (response) {
                    var trHTML = '';
                    files = response.files;
                    $.each(response.files, function (i, item) {
                        trHTML += '<tr><td>' + item.name + '</td><td>' + item.lastModifiedDate + '</td><td><label><input class="with-gap" id="rbtnFileSelected' + i + '" value="' + i + '" name="rbtnFileSelected" type="radio"/><span></span></label></td></tr>';
                    });
                    $('#filesList').html(trHTML);
                    $('input[type=radio][name=rbtnFileSelected]').on('change', function (data) {
                        $('#fileNameToSave').val(response.files[$(this).val()].name);
                        updateSelectedFileRowEvent();
                        setLoadButtonState();
                    });
                    updateSelectedFileRow();
                },
                error: function (xhr, textStatus, errorThrown) {
                    window.alert('Files request failed.' + errorThrown, 'error');
                }
            });
        }

        svgEditor.setCustomHandlers({
            open: function(){
                $('.ui-dialog-buttonpane').find('button:nth-child(2)').css('visibility','hidden');
                $('.ui-dialog-buttonpane').find('button:nth-child(1)').css('visibility','visible');
                $('#fileNameToSave').prop('readonly', true);
                $('#fileNameToSave').prop('placeholder', "");
                loadFilesList();
                setLoadButtonState();
                fileDialog.dialog("open");
            },
            save: function(win, data) {
                $('.ui-dialog-buttonpane').find('button:nth-child(1)').css('visibility','hidden');
                $('.ui-dialog-buttonpane').find('button:nth-child(2)').css('visibility','visible');
                $('#fileNameToSave').prop('readonly', false);
                loadFilesList();
                validateFileName();
                svgData ="<?xml version=\"1.0\"?>\n" + data;
                fileDialog.dialog("open");
            }
        });
        $('#fileNameToSave').on('keyup', updateSelectedFileRowEvent);
        $('#fileNameToSave').on('change', updateSelectedFileRowEvent);
        $('#fileNameToSave').on('blur', updateSelectedFileRowEvent);


        fileDialog = $( "#file-dialog" ).dialog({
            autoOpen: false,
            height: 400,
            width: 700,
            modal: true,
            buttons: {
                Load: function() {
                    var selectedItem = $('input[type=radio][name=rbtnFileSelected]:checked');
                    if(selectedItem == null || selectedItem.length<1) return;
                    $.ajax({
                        type: 'GET',
                        dataType: 'text',
                        url: 'http://'+location.hostname+':8000/svgs/'+encodeURI(files[selectedItem[0].value].name),
                        timeout: 5000,
                        cache:false,
                        async: false,
                        success: function (response) {
                            try {
                                svgCanvas.clear();
                                svgCanvas.setSvgString(response);
                                svgEditor.updateCanvas();
                            } catch (e) {
                                window.alert('Error loading  SVG:\n' + e, 'error');
                                return;
                            }
                        },
                        error: function (xhr, textStatus, errorThrown) {
                            window.alert('Files request failed.' + errorThrown, 'error');
                        }
                    });
                    fileDialog.dialog( "close" );
                },
                Save: function(win, data) {
                    if(!$('#fileNameToSave')[0].checkValidity()){
                        $('#fileNameToSave')[0].reportValidity();
                        return;
                    }
                    var fileName = $('#fileNameToSave').val().toString();
                    var formData = new FormData();
                    formData.append("fileName",fileName);
                    formData.append("fileContent",svgData);
                    $.ajax({
                        url:"http://"+location.hostname+":8000/svgs/upload",
                        data:formData,
                        type: 'POST',
                        dataType: 'json',
                        cache: false,
                        contentType: false,
                        processData:false,
                        success: function(data, textStatus, jqXHR){
                            window.alert('Saved');
                        },
                        error: function(jqXHR, textStatus, errorThrown){
                            window.alert('Failed to save.' + errorThrown, 'error');
                        }
                    });

                    fileDialog.dialog( "close" );
                },
                Cancel: function() {
                    fileDialog.dialog( "close" );
                }
            },
            close: function() {
                //form[ 0 ].reset();
                //allFields.removeClass( "ui-state-error" );
            }
        });


        //     "            <div class=\"modal-content\">\n" +
        //     "            <table style=\"margin-bottom:30px\">\n" +
        //     "            <thead>\n" +
        //     "            <tr>\n" +
        //     "            <th>File name</th>\n" +
        //     "        <th>Modified On</th>\n" +
        //     "        <th></th>\n" +
        //     "        </tr>\n" +
        //     "        </thead>\n" +
        //     "        <tbody id=\"filesList\"></tbody>\n" +
        //     "            </table>\n" +
        //     "            <div class=\"row\" id=\"fileNameToSaveRow\">\n" +
        //     "            <div class=\"input-field col s6\">\n" +
        //     "            <label class=\"active\" for=\"fileNameToSave\">File Name</label>\n" +
        //     "        <input placeholder=\"NewFileName.xml\" id=\"fileNameToSave\" data-length=\"30\" type=\"text\" class=\"validate\" required pattern=\"^[A-Za-z0-9-_,\\s]+[.][Xx][Mm][Ll]\">\n" +
        //     "            <span class=\"helper-text\" data-error=\"Need a valid XML file name\" ></span>\n" +
        //     "            </div>\n" +
        //     "            </div>\n" +
        //     "            </div>\n" +
        //     "            <div class=\"modal-footer\">\n" +
        //     "            <a class=\"modal-action modal-close waves-effect waves-red btn red lighten-2\">Cancel</a>\n" +
        //     "            <a id=\"loadFileButton\" class=\"modal-action modal-close waves-effect waves-green btn\">Load</a>\n" +
        //     "            <a id=\"saveFileButton\" class=\"modal-action modal-close waves-effect waves-green btn\">Save</a>\n" +
        //     "            </div> \n" +
        //     "        </div>";
        //
        // $("#svg_editor").show().prepend(fileDialog);




    }
});
