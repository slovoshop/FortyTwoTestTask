
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
       var msgArray = data.message.split("^");

       $billboard.append('<br/><b>' + 
                        msgArray[0] + '</b> ' +
                        msgArray[2] + '<br>' +
                        msgArray[3]);
       $billboard.scrollTop($billboard.scrollTop() + 25);

       localStorage.setItem('newMessage', data.message);
    });
}


function receiveMessage(msg) { 
  if (msg.key == 'newMessage') {

    msgArray = msg.newValue.split("^");

    $billboard.append('<br/><b>' + 
                     msgArray[0] + '</b> ' +
                     msgArray[2] + '<br>' +
                     msgArray[3]);
    $billboard.scrollTop($billboard.scrollTop() + 25);

    if (!chatFocused) {
      unread++;
      $('title').text("(" + unread + ") unread");
    }
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


$(document).ready(function() {

  var ws4redis = WS4Redis({
    uri: '{{ WEBSOCKET_URI }}dialogs?subscribe-user',
    receive_message: receiveMessage,
    heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
  });

  $('#send_message').click(sendMessage);

  $message.keydown(function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      sendMessage();
    }
  });

  window.addEventListener("storage", receiveMessage, false);

});
