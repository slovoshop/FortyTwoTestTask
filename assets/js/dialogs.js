
var billboard = $('#billboard');

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

  msg = $('#user').val() + '^' +
        now.toLocaleString("en-US", dateOptions) + '^' +
        $('#text_message').val();

  localStorage.setItem('newMessage', msg);
  console.log(msg);
}


$(document).ready(function() {

  $('#send_message').click(sendMessage);

  $("#text_message").keydown(function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      sendMessage();
    }
  });

});
