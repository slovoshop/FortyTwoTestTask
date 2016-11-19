
$(document).ready(function() {

  var config = {
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

  $.validate({
     modules : 'jsconf',
     onModulesLoaded : function() {
       $.setupValidation(config);
     }
  }); 

});
