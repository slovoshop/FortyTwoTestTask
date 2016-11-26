
var billboard = $('#billboard');
var msgArray;

		var dateOptions = {
			month:  'short',
			day:    'numeric',
			year:   'numeric',
			hour:   '2-digit',
			minute: '2-digit',
			second: '2-digit',
		};


function sendMessage() {
  var now = new Date();

  var msg = $('#text_message').data('sender') + '^' +
            $('#user').val() + '^' +
            now.toLocaleString("en-US", dateOptions) + '^' +
            $('#text_message').val();

  localStorage.setItem('newMessage', msg);

  msgArray = msg.split("^");

  billboard.append('<br/><b>' + 
                     msgArray[0] + '</b> ' +
                     msgArray[2] + '<br>' +
                     msgArray[3]);
  billboard.scrollTop(billboard.scrollTop() + 25);
}


function receiveMessage(msg) { 
  if (msg.key == 'newMessage') {

    msgArray = msg.newValue.split("^");

    billboard.append('<br/><b>' + 
                     msgArray[0] + '</b> ' +
                     msgArray[2] + '<br>' +
                     msgArray[3]);
    billboard.scrollTop(billboard.scrollTop() + 25);
  } 
} 


$(document).ready(function() {

  $('#send_message').click(sendMessage);

  $("#text_message").keydown(function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      sendMessage();
    }
  });

  window.addEventListener("storage", receiveMessage, false);

});
