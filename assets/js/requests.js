
var $initTitle = $('title').text();
var checkReqTmr; // timer for checking request's logs
var unread = 0;


function toDate(dateStr) {  
 // convert "yyyy-mm-dd hh:mm:ss" string to date

		var dateOptions = {
			month:  'short',
			day:    'numeric',
			year:   'numeric',
			hour:   '2-digit',
			minute: '2-digit',
			second: '2-digit',
		};

    var yyyymmdd = dateStr.substring(0, 10);
    var time = dateStr.substring(11, 19);
    var dateArray = yyyymmdd.split("-");
    var timeArray = time.split(":");

    result = new Date(
                      dateArray[0], 
                      dateArray[1] - 1, 
                      dateArray[2],
                      timeArray[0],
                      timeArray[1],
                      timeArray[2]
                 );

    var now = new Date();
    result.setHours(result.getHours() - now.getTimezoneOffset()/60);

    return result.toLocaleString("en-US", dateOptions);
}


function JsonRequests() {
  var currentUrl = location.href;

	$.ajax({
    type: 'GET',
    url: currentUrl,
	  cache: false,
	  success: function(data){
               var newContent;
               for (var i = 1; i <= data.length; i++) 
                 newContent += '<tr><td>' + i + '</td>' +
                               '<td>' + data[i-1].fields.method + '</td>' +
                               '<td>' + data[i-1].fields.path + '</td>' +
                               '<td>' + data[i-1].fields.status_code + '</td>' +
                               '<td>' + toDate(data[i-1].fields.date) + '</td></tr>';
               
               $('#requests-content').html(newContent);
               if (localStorage.synchronizePages == 'false') {
                 unread++;
                 $(document).attr("title", "(" + unread + ") unread");
               }
    },

    error: function(xhr, status, error){
		    console.log(error);
    }
  });
}


window.onfocus = function() {
  localStorage.setItem('synchronizePages', true);
  clearTimeout(checkReqTmr);
  $('title').text($initTitle);
};


window.onblur = function() {
  localStorage.setItem('synchronizePages', false);
  unread = 0;
  checkReqTmr = setInterval(JsonRequests, 1500);
}


window.addEventListener(
   "storage", 

   function() {
     if (localStorage.synchronizePages == 'true') {
         clearTimeout(checkReqTmr);
         $('title').text($initTitle);
       } else {
         unread = 0;
         checkReqTmr = setInterval(JsonRequests, 1500);
     }
   }, 

   false
);


$(document).ready(function(){
  localStorage.setItem('synchronizePages', true);
});
