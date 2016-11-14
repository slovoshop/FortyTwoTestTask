
function blockPage() {

  if( $('#failmessage').length ) {
    $('#failmessage').remove();
    $('#after_fail_empty_string').remove();
    $('div .form-group').removeClass('has-error');
    $('span').remove();
  } 

  $('textarea').attr('disabled', 'disabled');
  $('input').attr('disabled', 'disabled');
  $('button').attr('disabled', 'disabled');
  $('a').attr('disabled', 'disabled');
  $('.loader').css('display', 'block');
}


function unblockPage() {
		$('textarea').removeAttr('disabled');
		$('input').removeAttr('disabled');
		$('button').removeAttr('disabled');
		$('a').removeAttr('disabled');
		$('.loader').css('display', 'none');
}


function fakeGoodSaving() {
  blockPage();
  setTimeout(hardcodedUpdate, 2000);
}


function fakeFailSaving() {
  blockPage();
  setTimeout(showErrors, 2000);
}


function hardcodedUpdate() {

  var profile = {
      pk: 2, 
      model: "hello.aboutme",
      fields: [{
          first_name: "Kim", 
          last_name: "Shao",  
          birthday: "1981-03-25", 
          email: "kim@box.com",
          jabber: "ks_jab", 
          skype: "ks_skype", 
          bio: "Senior Django developer", 
          contacts: "facebook.com/kim"
      }]
  };

  $.ajax({
  url: $(this).attr("href"),
  cache: false,

  success: function(){

      for(field in profile.fields[0]) 
        $('#id_' + field).val(profile.fields[0][field]);

      unblockPage();
      var message = "<div id='goodmessage' class='col-xs-12" +
                    " bg-success prof_updated'>" +
                    "Changes have been save!</div><br><br>";
      $('.loader').before(message);

      setTimeout(function() {
        $('#goodmessage').remove();
        $('#edit-content-column br').eq(0).remove();
        $('#edit-content-column br').eq(0).remove();
        }, 2000);
		},

  error: function(error){
      unblockPage();
      console.log(error);
    }
	});
}


$("#saveBtn").click(function(event) {
  event.preventDefault();
  fakeGoodSaving();
});


$("#errBtn").click(function(event) {
  event.preventDefault();
  fakeFailSaving();
});


function showErrors() {
  var errors = {
        first_name: "This field is required",  
        last_name:  "This field is required",
        birthday:   "Enter a valid date", 
        email:      "Enter a valid email address",
        jabber:     "This field is required",
        skype:      "This field is required"
      };

	$.ajax({
	url: $(this).attr("href"),
	cache: false,

	success: function(){
      unblockPage();
      var message = "<div id='failmessage' class='col-xs-12'>" +
                    "<b>Check errors, please!</b></div>";
      $('.loader').before(message);
      $('#failmessage').after("<p id='after_fail_empty_string'>&nbsp</p>");

			var $idElement, $labelElement;

			for(field in errors) {
				$idElement = $('#id_' + field);
				$idElement.parent('div').prepend('<span>&nbsp'+errors[field]+'</span>');
        if(errors[field]) {
				  $labelElement = $("label[for='"+$idElement.attr('id')+"']").prepend('<span>*</span>');
				  $labelElement.parent('div').addClass('has-error')
          }
			  }
		  },

  error: function(error){
      unblockPage();
		  console.log(error);
      }
	});
}


function customizePhotoDiv() {
  $photoDiv = $('input[name="photo"]').parent('div');
  $photoDiv.find('a').hide(); // hide imagelink

  $photoDiv.contents().filter(function() {
    return this.nodeType===3; // remove text from div
  }).remove();
}


// Change image when user select another file

$("#id_photo").change(function() {
  var input = this;

  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      $(".picture").attr('src', e.target.result);
    }

    reader.readAsDataURL(input.files[0]);
  }
});

// Change image to default when user clear image in edit.html

$('input[name="photo-clear"]').click(function() {
  $('input[name="photo"]').parent('div').hide();
  $('label[for="id_photo"]').after('<div><br><br></div>');
  $(".picture").attr('src', '/static/img/user_default.png');
}); 


$(document).ready(function() {

  var config = {         /* http://www.formvalidator.net */
    form : 'form',
    validate : {
      '#id_first_name, #id_last_name' : {
        validation : 'length',
        length : 'min3'
      },
      '#id_email, #id_jabber' : {
        validation : 'email'
      },
      '#id_birthday' : {
        validation : 'birthdate',
        'error-msg' : 'Date should be younger than today and not older than 120 years'
      }
    },
    onElementValidate : function(valid, $el, $form, errorMess) {
       $rowDiv = $el.parents().eq(3);
       if(valid) {
         $rowDiv.removeClass('errorspacing');
       } else {
         $rowDiv.addClass('errorspacing');
       }
    }
  };


  $.validate({
     modules : 'jsconf, date',
     onModulesLoaded : function() {
       $.setupValidation(config);
     }
  }); 


  $( function() {
    $("#id_birthday").datepicker();
    $( "#id_birthday" ).datepicker("option", "dateFormat", "yy-mm-dd");
    $("#id_birthday").datepicker("setDate" , "2016-01-01");
  });

  customizePhotoDiv();

});
