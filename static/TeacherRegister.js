function validateForm() {
    var fname;
    var lname;
    var mname;
    var dob;
    var age;
    var email;
    var pwd;
    var cpwd;
    email = document.forms["homePageForm"]["email"].value;
    pwd = document.forms["homePageForm"]["password"].value;
    //console.log(name);
    if (email.length == 0) {
        document.getElementById("email_info").innerHTML = "Enter Email ID";
        return false;
    }
    if (pwd.length == 0) {
        document.getElementById("password_info").innerHTML = "Enter Password";
        return false;
    }
}