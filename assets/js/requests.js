
var $initTitle = $('title').text();
var checkReqTmr; // timer for checking request's logs
var unread = 0;


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
                               '<td>' + data[i-1].method + '</td>' +
                               '<td>' + data[i-1].path + '</td>' +
                               '<td>' + data[i-1].status_code + '</td>' +
                               '<td>' + data[i-1].date + '</td></tr>';
               
               $('#requests-content').html(newContent);
               unread++;
               if (localStorage.synchronizePages == 'false') {
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
  console.log("SP = true");
};


window.onblur = function() {
  localStorage.setItem('synchronizePages', false);
  unread = 0;
  checkReqTmr = setInterval(JsonRequests, 1500);
  console.log("SP = true");
}


window.addEventListener(
   "storage", 

   function() {
     if (localStorage.synchronizePages == 'true') {
         clearTimeout(checkReqTmr);
         $('title').text($initTitle);
         console.log("SP = true");
       } else {
         unread = 0;
         checkReqTmr = setInterval(FakeRequests, 1500);
         console.log("SP = true");
     }
   }, 

   false
);


$(document).ready(function(){
  localStorage.setItem('synchronizePages', true);
  console.log("doc ready");
});
