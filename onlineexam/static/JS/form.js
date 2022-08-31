function checkPasswordStrength() {
    var number = /([0-9])/;
    var alphabets = /([a-zA-Z])/;
    var special_characters = /([~,!,@,#,$,%,^,&,*,-,_,+,=,?,>,<])/;
    if ($('#password').val().length < 6) {
        $('#password-strength-status').removeClass();
        $('#password-strength-status').addClass('weak-password');
        $('#password-strength-status').html("Weak (should be atleast 6 characters.)");
    } else {
        if ($('#password').val().match(number) && $('#password').val().match(alphabets) && $('#password').val().match(special_characters)) {
            $('#password-strength-status').removeClass();
            $('#password-strength-status').addClass('strong-password');
            $('#password-strength-status').html("Strong");
        } else {
            $('#password-strength-status').removeClass();
            $('#password-strength-status').addClass('medium-password');
            $('#password-strength-status').html("Medium (should include alphabets, numbers and special characters.)");
        }
    }
}

function checkPassword() {
    if (($('#password').val().length == 0) || ($('#Confirm_password').val().length == 0)) {
        $('#password-status').removeClass()
        $('#password-status').addClass("weak-password")
        $('#password-status').html("Password field is empty")
    } else {
        if (($('#password').val()) == ($('#Confirm_password').val())) {
            $('#password-status').removeClass()
            $('#password-status').addClass("strong-password")
            $('#password-status').html("Password matched")
        } else {
            $('#password-status').removeClass()
            $('#password-status').addClass("weak-password")
            $('#password-status').html("Password doesn't match")
        }
    }
}

$(document).ready(function(event){

});

function validateForm(){
    let email, f_name, m_name, l_name, dob, profile_pic, pwd, cnf_pwd ;

    email = document.forms["registration_form"]["email"].value;
    f_name = document.forms["registration_form"]["first_name"].value;
    m_name = document.forms["registration_form"]["middle_name"].value;
    l_name = document.forms["registration_form"]["last_name"].value;
    dob = document.forms["registration_form"]["dob"].value;
    pwd = document.forms["registration_form"]["password"].value;
    cnf_pwd = document.forms["registration_form"]["Confirm_password"].value;
    profile_pic = document.forms["registration_form"]["profile_pic"].value;


    const email_validation = / [a-zA-Z0-9]+\@[a-zA-Z0-9]+\.[a-z]+/;
    const name_validation = /[a-zA-Z]+/;
    const image_arr = new Array("png", "jpeg", "jpg");

    let exten = profile_pic.split('.').pop();

    if(!f_name.match(name_validation))
    {
        document.getElementById("err_msg").innerHTML = "First Name Empty";
        return false;       
    }
    else if(!m_name.match(name_validation))
    {
        document.getElementById("err_msg").innerHTML = "Middle Name Empty";
        return false;       
    }
    else if(!l_name.match(name_validation))
    {
        document.getElementById("err_msg").innerHTML = "Last Name empty";
        return false;       
    }
    else if(dob.length == 0)
    {
        document.getElementById("err_msg").innerHTML = "No Date Of Birth Provided";
        return false;        
    }
    else if(pwd != cnf_pwd)
    {
        document.getElementById("err_msg").innerHTML = "Password Doesn't Match";
        return false;    
    }
    else if (email.length == 0) {
        document.getElementById("err_msg").innerHTML = "Email Id column empty";
        return false;
    }
    else if((email.length>0 && email.match(email_validation)) == false)
    {
        document.getElementById("err_msg").innerHTML = "Invalid email id";
        return false;       
    }

    for(let i=0; i<3; i++)
    {
        if(exten == image_arr[i]){
            console.log(exten == image_arr[i]);
            return true;
        }
    }
    
    document.getElementById("err_msg").innerHTML = "Upload Correct image";
    return false;

}