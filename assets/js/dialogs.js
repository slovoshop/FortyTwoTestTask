/*global $, _ */
$(function() {

    var textarea = $('div#chat');
    var input = $('input#input');

    var remove_spinner = function() {
        if (textarea.hasClass('spinner'))
            textarea.removeClass('spinner');
    };

    remove_spinner();
    input.focus();

});
