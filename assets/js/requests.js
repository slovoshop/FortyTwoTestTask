
var onLoadRequestsDB = 0; // get requests count in DB after window.onload
var ajaxRequestsDB = 0;   // get requests count in DB after current AJAX
var firstAJAX = false;    // init first ajax after loading request.html
var checkReqTmr;          // timer for checking request's logs

var sortingURL = '';
var $dateColumn = $('#dateColumn');
var $priorityColumn = $('#priorityColumn');

var $initTitle = $('title').text();

var $reqEditBox = $('#request_edition');
var reqEditID = '/'; // request ID for the req_edit_form


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
  $.ajax({
    type: 'GET',
    url: sortingURL,
    cache: false,
    dataType: 'json',

    beforeSend: function(xhr, settings){

        if (sortingURL == location.href) {
          $('a.sort span').hide();
          $('span#defaultDate').show();
          $('span#defaultPriority').show();
        }

        $('a').attr('disabled', 'disabled');
        console.log('sortingURL: ' + sortingURL);
    },

    success: function(data, status, xhr){

        ajaxRequestsDB = data.dbcount;
		   
        if (firstAJAX) {
          onLoadRequestsDB = ajaxRequestsDB;
          firstAJAX = false;
        }

        var unreadRequests = ajaxRequestsDB - onLoadRequestsDB;

        if (!unreadRequests || (localStorage.synchronizePages == 'true')) {
          $('title').text($initTitle);
        } else {
          $('title').text("(" + unreadRequests + ") unread");
        }

        /* AJAX get data in JSON like that:
        {"dbcount": 701, 
         "reqlogs": [
                    {"date": "2016-09-16 09:20:19.098777+00:00", 
                     "path": "http://localhost:8000/request/", 
                     "status_code": 200, 
                     "priority": 2,
                     "id": 701, 
                     "method": "GET"}, 
                    .....
                    {"date": "2016-09-16 09:20:12.355412+00:00", 
                     "path": "http://localhost:8000/admin/", 
                     "status_code": 200, 
                     "priority": 7,
                     "id": 700, 
                     "method": "GET"}
                    ]
        }*/

        if (data.dbcount) {
          $('#db_has_entries').show();
          $('#db_is_empty').hide();
        } else {
          $('#db_has_entries').hide();
          $('#db_is_empty').show();          
        }

        var newContent;
        for (var i = 1; i <= data.reqlogs.length; i++) 

          newContent += '<tr><td>' + i + '</td>' +
            '<td>' + data.reqlogs[i-1].method + '</td>' +
            '<td>' + data.reqlogs[i-1].path + '</td>' +
            '<td>' + data.reqlogs[i-1].status_code + '</td>' +
            '<td>' + toDate(data.reqlogs[i-1].date) + '</td>' +
            '<td style="text-align: center;"><a class="priority"' +
            ' id="priority_' + data.reqlogs[i-1].id + 
            '" href="/request/edit/' + data.reqlogs[i-1].id +
            '" data-request-id="' + data.reqlogs[i-1].id + '">' + 
            data.reqlogs[i-1].priority + '</a></td></tr>';

        $('#requests-content').html(newContent);
        $('a').removeAttr('disabled');
    },

    error: function(xhr, status, error){

        $('a').removeAttr('disabled');
        console.log(error);
    }
  });
}


window.onfocus = function() {
  clearTimeout(checkReqTmr);
  if ($reqEditBox.is(':visible')) return;

  localStorage.setItem('synchronizePages', true);
  firstAJAX = true;
  JsonRequests();
  $('title').text($initTitle);
};


window.onblur = function() {
  localStorage.setItem('synchronizePages', false);
  if ($reqEditBox.is(':visible')) return;

  checkReqTmr = setInterval(JsonRequests, 1500);
}


$(document).on('click', 'a.priority', function() {
  
  $('#db_has_entries, #db_is_empty').hide();
  $reqEditBox.show();

  reqEditID = $(this).data('request-id');

  $("#request_edition").load('/request/edit/' +reqEditID+ ' #req_edit_form', 
    function() {

      var config = { /* http://www.formvalidator.net */
        form : 'form',
        validate : {
            '#id_priority' : {
            'validation' : 'number',
            'allowing': 'range[0;10]',
            'error-msg': 'Number must be in range 0-10'
            },
            '#id_status_code' : {
            'validation' : 'number'
            },
            '#id_method' : {
            'validation' : 'length',
            'length' : '3-6',
            'error-msg': 'Enter one of GET, POST, PUT, DELETE'
            }
        }
      };

      $.setupValidation(config);
      $.validate(); 

    });
  
  return false;
});


$(document).on('click', '#req_edit_form a', function() {

  $("#request_edition").hide();
  $('#db_has_entries').show();

  return false;
});


window.addEventListener(
   "storage", 

   function() { 
     if (localStorage.synchronizePages == 'true') {
        firstAJAX = true;
        JsonRequests();
        clearTimeout(checkReqTmr);
        $('title').text($initTitle);
     } else if (localStorage.synchronizePages == 'false') {
         checkReqTmr = setInterval(JsonRequests, 1500);
     }
   }, 

   false
);


$('a.sort').click(function() {
/* AJAX sorting requests by priority or date  */

  if ($(this).is($dateColumn)) {

    $priorityColumn.html('Priority');

    if (sortingURL.includes("?date=0")) {
      sortingURL = location.href + '?date=1';
      $dateColumn.html('Date&amp;Time&uarr;');
    } else if(sortingURL.includes("?date=1")) {
      sortingURL = location.href + '?date=0';
      $dateColumn.html('Date&amp;Time&darr;');
    } else {
      sortingURL = location.href + '?date=0';
      $dateColumn.html('Date&amp;Time&darr;');
    }
  } 

  if ($(this).is($priorityColumn)) {

    $dateColumn.html('Date&amp;Time');

    if (sortingURL.includes("?priority=0")) {
      sortingURL = location.href + '?priority=1';
      $priorityColumn.html('High Priority&uarr;');
    } else if(sortingURL.includes("?priority=1")) {
      sortingURL = location.href + '?priority=0';
      $priorityColumn.html('Low Priority&darr;');
    } else {
      sortingURL = location.href + '?priority=1';
      $priorityColumn.html('High Priority&uarr;');
    }
  }

  JsonRequests();
  return false;
});


$(document).ready(function(){

  /* when events 'onfocus' and 'ready' follow each other 
     than we set synchronizePages=true two times.
     And EventListener("storage") is not activated for the second time,
     because of 'true, true' sequence. So we must reset synchronizePages
     by setting 'true, other value, true' sequence*/

  localStorage.setItem('synchronizePages', '');
  localStorage.setItem('synchronizePages', true);
  firstAJAX = true;
  sortingURL = location.href;
  JsonRequests();

  $.validate({
     modules : 'jsconf', // module needed for the request validation
  }); 

});
