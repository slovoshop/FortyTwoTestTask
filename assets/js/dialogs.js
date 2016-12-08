
var $billboard = $('#billboard'),
    $message = $("#text_message"),
    $initTitle = $('title').text();

var msgArray, 
    chatFocused,
    unread = 0;

var	dateOptions = {
			month:  'short',
			day:    'numeric',
			year:   'numeric',
			hour:   '2-digit',
			minute: '2-digit',
			second: '2-digit',
		};


function sendMessage() {
}


function receiveMessage(msg) { 
} 


window.onfocus = function() {
  chatFocused = true;
  $('title').text($initTitle);
  unread = 0;
};


window.onblur = function() {
  chatFocused = false;
};

