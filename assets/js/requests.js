
var $initTitle = $('title').text();
var checkReqTmr; // timer for checking request's logs
var unread = 0;

var content = '';
for(var num = 1; num <= 10; num++) {
  content += '<tr><td>' + num + '</td>' + 
             '<td>GET</td>' +
             '<td>/request/</td>' + 
             '<td>200</td>' +
             '<td>November 07, 2016, 14:05 a.m.</td></tr>';
}


function FakeRequests() {
	$.ajax({
	url: $(this).attr("href"),
	cache: false,
	success: function(data){
           $('#requests-content').html(content);
           unread++;
           if (localStorage.synchronizePages == 'false') {
             $(document).attr("title", "(" + unread + ") unread");
           }
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
  checkReqTmr = setInterval(FakeRequests, 1500);
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
