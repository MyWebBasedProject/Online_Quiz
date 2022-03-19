function validateForm() {

    var email;
    var pwd;
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
    var getSelectedValue = document.querySelector('input[name="category"]:checked');
    if (getSelectedValue == null) {
        alert("Please select Category");
        return false;
    }
}