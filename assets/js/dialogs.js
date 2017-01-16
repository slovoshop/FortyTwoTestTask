/*global $, _ */
$(function() {
    "use strict";

    var initTitle = $('title').text(),
        textarea = $('div#chat'), // place for messages
        dialogsList = $('#threads'), //left-handed threads list
        input = $('input#input'), // input here new message
        btn_send = $('button[id=btn_send]'), // button to send message
        in_unload = false, // stop functions during page unloading
        selectedPartner,
        serviceText, // used to change dialog by clicking partner link
        lastid_buffer, 
        scan_messages_marker, // used to check if another thread is selected
        chatFocused,
        totalUnread;

    // Dict with unread messages like {'partner1': unread1, 'partner2': unread2}
    var unread = {};

    // Сurrent partner for communication
    var currentPartner = input.data('sender');
    var currentThreadID = 0;

    // value can be 'changeDialog' or 'currentDialog'
    var mode = 'currentDialog'; 

    /* Contains the current number of failed requests (for get_new_messages) in a row. */
    var failed_requests_in_a_row = 0;

    /* remove parentheses () from the left-handed dialogs list */
    $('a.thread-link').html(function(i, html) {
        return html.replace(/\(\)/, '');
    });
    dialogsList.show();

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


    // hide loaders image
    var remove_spinner = function() {
        textarea.removeClass('spinner');
        dialogsList.removeClass('spinner1');
    };

    remove_spinner();
    input.focus();


    // Click-handler for Send button.
    btn_send.click(function(event) {

        event.preventDefault();
        btn_send.addClass('disabled');
        textarea.addClass('spinner');

        selectedPartner = $('#recipient-select').val();

        if (selectedPartner !== currentPartner) {
            mode = 'changeDialog';
            lastid_buffer = -1;
            $('a.thread-link').hide();

            if ($('#no_threads').length) $('#no_threads').remove();
            else dialogsList.addClass('spinner1');

            textarea.html('');
        }

        $.post('/send/', {

            'text': input.val(),
            'sender_id': input.data('senderid'),
            'recipient': selectedPartner,
            'mode': mode

        }, function(data, status, xhr) {

            if (mode == 'changeDialog') {
                serviceText = 'OK';
                console.log('service message: switch to thread "' + 
                            input.data('sender') + '-' + selectedPartner + '"');
            }

            if (xhr.getResponseHeader('content-type') === 'application/json')
                if (lastid_buffer === -1) switch_to_another_chat(data);
                else add_error("Invalid message: " + data.text[0]);

        }).fail(function(data) {

            // Show the response text as plaintext.
            var status = data.status;
            var statusText = data.statusText;

            // If we've hit a 400 (Bad Request), show the responseText.
            if (status === 400) statusText += ": " + data.responseText;
            add_error(status + " " + statusText);

        }).always(function() {
            btn_send.removeClass('disabled');
            if (mode == 'currentDialog') textarea.removeClass('spinner');
            else mode = 'currentDialog';
            input.val('');
            input.focus();

            if (serviceText !== 'OK') {
                textarea.html('');
                failed_requests_in_a_row = 0;
                add_error('No response from the server. Try to click partner link later!');
                $('a.thread-link').show();
            }
        });

        return false;
    });


    // handle enter in the input field to click the "Send" button.
    input.keypress(function(event) {
        if (event.which === 13) {
            event.preventDefault();
            btn_send.click();
            return false;
        }
        if (event.which === 38) { // press &(ampersand) to test something
            $.post('/send/', {
                'text': 'test',
                'sender_id': 3,
                'recipient': 'admin',
                'mode': 'currentDialog'
            }, function(data, status, xhr) {
                console.log('test message from Andrey to admin was sent');
            });
        }

        return true;
    });


    /* Change dialog by clicking partner link */
    $(document).on('click', 'a.thread-link', function() {

        if (btn_send.hasClass('disabled')) return false;

        var newPartner = $(this).data('partner');

        if (newPartner !== currentPartner) {
            $('#recipient-select').val(newPartner);
            serviceText = 'changeDialog to ' + input.data('sender') + '-' + newPartner;
            input.val(serviceText);
            btn_send.click();
        }

        return false;
    });


    /* Correct HTML after dialog changing */
    var switch_to_another_chat = function(data) {
        if (in_unload)
            return;

        // This happens when the user sends an incorrect message after page loading
        if(data.hasOwnProperty('text')) {
            add_error("Invalid message: " + data.text[0]);
            return;
        }

        _.each(data.threads, function(thread) {
            if (thread.partner === selectedPartner) {
                $('#currentDialog').text(input.data('sender') + '-' + selectedPartner);
                currentThreadID = thread.thread;
            }
        });

        unread[selectedPartner] = 0;
        currentPartner = selectedPartner;

        // Start long polling with new thread
        scan_messages_marker = setTimeout(get_new_messages, 200);
        input.focus();
    };


    /* Display error after bad request */
    var add_error = function(data) {
        if (in_unload)
            return;

        remove_spinner();

        if (failed_requests_in_a_row > 3) {
            var lastChatLine = textarea.find('pre').last().text();

            if(lastChatLine.indexOf('try again') === -1)
                data = "Reached the max number of failed requests in a row.<br />" +
                "Click <a href=\"javascript:$.retry_get_new_messages();\">Here</a> to try again!";
            else return;
        }

        var line = '<span class="error"><span class="bold">Error</span>:<br /><pre>' +
            data + '</pre></span>';
        textarea.append(line);
        textarea.scrollTop(textarea[0].scrollHeight);
    };


    /* Gets new messages from the server by initiating an AJAX POST-request.
     * If any new message(s) was found, some JSON in returned.
     * After 3 failed requests in a row, the loop is stopped.
     */
    var get_new_messages = function() {
        
        // Remember the request until the function is executed 
        var stored_scan_messages_marker = scan_messages_marker;

        if (failed_requests_in_a_row > 3) return;

        //if (lastid_buffer === -1) unread[selectedPartner] = 0;

        $.post('/get_new/', 
        {
            'thread_id': currentThreadID,
            'username': input.data('sender'),
            'receiver': currentPartner,
            'lastid_buffer': lastid_buffer,
            'unread_dict': JSON.stringify(unread)
 
        }, function(result) { 

            console.log('scan_status: ' + result.scan_status + 
                        ' (lastid_buffer = ' + lastid_buffer + ')');

            if (scan_messages_marker != stored_scan_messages_marker) return;

            if (failed_requests_in_a_row > 3) return;
            else failed_requests_in_a_row = 0;

            if (result.scan_status === 'Update threads list')
                update_threads_menu(result.threads);

            if (result.scan_status === 'Last messages after dialog changing' ||
                result.scan_status === 'Current dialog contains new messages') {
                lastid_buffer = result.lastid;    
                add_messages(result.messages);
            }

            if (result.scan_status === 'LP-cycle is ended without new messages') return;
               
        }).fail(function(data) {

            /* A fail has happened, increment the counter. */
            failed_requests_in_a_row += 1;

            if (scan_messages_marker != stored_scan_messages_marker) return;

            /* Format the error string into something readable, instead of [Object object]. */
            var failed_string = data.status + ": " + data.statusText;
            add_error(failed_string);

            /* Seems to happen on hibernate, the request will restart. */
            if (data.status === 0) return;

        }).always(function() {

           if (scan_messages_marker == stored_scan_messages_marker)
               scan_messages_marker = setTimeout(get_new_messages, 200);
        });
    };


    // Renders updated left-handed menu with dialogs list
    var update_threads_menu = function(threads) {

            totalUnread = 0;

            _.each(threads, function(thread) {
                unread[thread.partner] = thread.unread;
                totalUnread += thread.unread;
            });

            if (!chatFocused && totalUnread !== 0)
                $('title').text('new (' +totalUnread+ ')');

            if (lastid_buffer === -1) {
                unread[selectedPartner] = 0;
                lastid_buffer = 0;
                dialogsList.removeClass('spinner1');
                textarea.removeClass('spinner');
            }

            /* Render left-handed dialogs list */
            var rendered_threads = _.template(
                '<% _.each(threads, function(thread) { %>' +
                    '<a class="thread-link" ' +
                    'data-thread="<%= thread.thread %>" ' +
                    'data-partner="<%= thread.partner %>"> ' + 
                    '<%= thread.partner %> (<%= thread.unread %>)</a><br><% }); %>')({
                threads: threads
            });

            /* remove parentheses with zero inside */
            rendered_threads = rendered_threads.replace(/\(0\)/g, '');

            $('div#threads').html(rendered_threads);
            $('a.thread-link[data-partner=' +selectedPartner+ ']').text(selectedPartner);
            $('a.thread-link[data-partner=' +selectedPartner+ ']').addClass('bold');
    };


    // convert timestamp to date in JavaScript
    var date_to_string = function(date) {
        var now = moment(); // moment.min.js
        if (now.year() === date.year()) {
            if (now.month() === date.month() && now.date() === date.date()) {
                return date.format('HH:mm');
            } else {
                return date.format('MM-DD HH:mm');
            }
        } else {
            return date.format('YYYY-MM-DD HH:mm');
        }
    };


    // Renders JSON messages to HTML and appends to the existing messages.
    var add_messages = function(messages) {
        if (in_unload)
            return;
        // Convert date objects to string repressentations.
        _.each(messages, function(message) {
            message.timestamp = moment(message.timestamp);
            message.formatted_timestamp = date_to_string(message.timestamp);
        });
        // Render the template using underscore.
        var rendered_messages = _.template(
            '<% _.each(messages, function(message) { %>' +
                '<span class="time">[<%= message.formatted_timestamp %>] </span>' +
                '<span class="username"><%= message.username %>:</span> ' +
                '<span class="message"><%= message.message %></span><br />' +
                '<% }); %>')({
            messages: messages
        });
        textarea.append(rendered_messages);
        textarea.scrollTop(textarea[0].scrollHeight);

        if (!chatFocused) {
            totalUnread += messages.length;
            $('title').text('new (' +totalUnread+ ')');
        }
    };


    /* Called by the user, if he/she wants to try and get new messages again
     * after the limit (failed_requests_in_a_row) has been exceeded.
     */
    $.retry_get_new_messages = function() {
        failed_requests_in_a_row = 0;
        var copyName = currentPartner;
        currentPartner = 'empty';
        $('a.thread-link[data-partner=' +copyName+ ']').click();
    };


window.onfocus = function() {
    chatFocused = true;
    $('title').text(initTitle);

    /* Remove from totalUnread new messages corresponding to current thread */
    totalUnread = 0;
    $.each(unread, function(index, value) { 
        totalUnread += unread[index];
    });
};


window.onblur = function() {
    chatFocused = false;
};


});
