$("#signup").click(function() {
    $("#first").fadeOut("fast", function() {
    $("#second").fadeIn("fast");
    });
    });
    
    $("#signin").click(function() {
    $("#second").fadeOut("fast", function() {
    $("#first").fadeIn("fast");
    });
    });
    
    
      
             $(function() {
               $("form[name='login']").validate({
                 rules: {
                   
                   email: {
                     required: true,
                     email: true
                   },
                   password: {
                     required: true,
                     
                   }
                 },
                  messages: {
                   email: "Please enter a valid email address",
                  
                   password: {
                     required: "Please enter password",
                    
                   }
                   
                 },
                 submitHandler: function(form) {
                   form.submit();
                 }
               });
             });
             
    
    
    $(function() {
      
      $("form[name='registration']").validate({
        rules: {
          firstname: "required",
          lastname: "required",
          email: {
            required: true,
            email: true
          },
          pass1: {
            required: true,
            minlength: 5
          },
          pass2: {
            required: true,
            equalTo: "[name='pass1']"
          },
        },
        
        messages: {
          firstname: "Please enter your firstname",
          lastname: "Please enter your lastname",
          pass1: {
            required: "Please provide a password",
            minlength: "Your password must be at least 5 characters long"
          },
          email: "Please enter a valid email address",
          pass1: {
            required: "Please provide a password",
            equalTo: "Passwords do not match"
          }
        },
      
        submitHandler: function(form) {
          form.submit();
        }
      });
    });
    