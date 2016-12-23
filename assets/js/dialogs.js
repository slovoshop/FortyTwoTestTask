/*global $, _ */
$(function() {
    "use strict";

    var textarea = $('div#chat'), // place for messages
        input = $('input#input'), // input here new message
        btn_send = $('button[id=btn_send]'), // button to send message
        currentThread = $('#currentDialog'), // from the left-handed panel
        in_unload = false, // stop functions during page unloading
        selectedPartner;

    // Сurrent interlocutor for communication
    var currentPartner = input.data('sender');

    // Set to true when send message into another (not current) thread
    var changeDialog = false; 

    // value can be 'changeDialog' or 'currentDialog'
    var mode = 'currentDialog'; 

    /* Contains the current number of failed requests (for get_new_messages) in a row. */
    var failed_requests_in_a_row = 0;

    // make sure AJAX-requests send the CSRF cookie, or the requests will be rejected.
    var csrftoken = $('input[type=hidden][name=csrfmiddlewaretoken]').val();

    $.ajaxSetup({
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    });


    // stop functions during page unloading
    $(window).bind('beforeunload', function() {
        in_unload = true;
    });

    // hide loader image
    var remove_spinner = function() {
        if (textarea.hasClass('spinner'))
            textarea.removeClass('spinner');
    };

    remove_spinner();
    input.focus();


    // Click handler for Send button.
    btn_send.click(function(event) {

        event.preventDefault();
        btn_send.addClass('disabled');

        selectedPartner = $('#recipient-select').val();
       
        if (selectedPartner !== currentPartner) {
            changeDialog = true;
            mode = 'changeDialog';
        }

        $.post('/send/', {

            'text': input.val(),
            'sender_id': input.data('senderid'),
            'recipient': selectedPartner,
            'mode': mode

        }, function(data, status, xhr) {

            if (xhr.getResponseHeader('content-type') === 'application/json')
                if (changeDialog) switch_to_another_chat(data);
                else add_error("Invalid message: " + data.text[0]);

            input.val('');
            input.focus();

        }).fail(function(data) {

            /* Show the response text as plaintext */
            var status = data.status;
            var statusText = data.statusText;

            /* If we've hit a 400 (Bad Request), show the responseText */
            if (status === 400) statusText += ": " + data.responseText;
            add_error(status + " " + statusText);

        }).always(function() {

            btn_send.removeClass('disabled');
            mode = 'currentDialog';
        });
        return false;
    });


    /* handle enter in the input field to click the "Send" button */
    input.keypress(function(event) {
        if (event.which === 13) {
            event.preventDefault();
            btn_send.click();
            return false;
        }
        if (event.which === 38) { // press &(ampersand) to test something
            //console.log(temp);
        }

        return true;
    });


    /* Display error after bad request */
    var add_error = function(data) {
        if (in_unload)
            return;
        var line = '<span class="error"><span class="bold">Error</span>:<br /><pre>' +
            data + '</pre></span>';
        textarea.append(line);
        textarea.scrollTop(textarea[0].scrollHeight);
    };


    /* Correct HTML after dialog changing */
    var switch_to_another_chat = function(data) {
        if (in_unload)
            return;

        textarea.html('');

        /* This happens when the user sends an incorrect message after page loading */
        if(data.hasOwnProperty('text')) {
            add_error("Invalid message: " + data.text[0]);
            return;
        }
      
        _.each(data.threads, function(thread) {
            if (thread.partner === selectedPartner) {
                currentThread.text(selectedPartner);
                currentThread.data('thread', thread.thread);
                currentThread.data('partner', thread.partner);
                currentThread.data('lastid', thread.lastid);
            }
        });

        currentPartner = selectedPartner;
        changeDialog = false;

        input.focus();
    };


});
