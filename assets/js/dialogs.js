
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

  var now = new Date();

  $.post(location.href, {
    sender: $message.data('sender'),
    receiver: $('#user').val(),
    date: now.toLocaleString("en-US", dateOptions),
    text: $message.val()})
    .done(function(data) {
       console.log('ajax post is OK');
    });
}


function receiveMessage(msg) { 

    msgArray = msg.split("^");

    $billboard.append('<br/><b>' + 
                     msgArray[0] + '</b> ' +
                     msgArray[1] + '<br>' +
                     msgArray[2]);
    $billboard.scrollTop($billboard.scrollTop() + 25);

    if (!chatFocused) {
      unread++;
      $('title').text("(" + unread + ") unread");
    } else {
      $('title').text($initTitle);
    }
} 


window.onfocus = function() {
  chatFocused = true;
  $('title').text($initTitle);
  unread = 0;
};


window.onblur = function() {
  chatFocused = false;
};

