

function validateForm() {

    var code;
    code = document.forms["quizloginForm"]["code"].value;
    if (code.length == 0) {
        document.getElementById("code_info").innerHTML = "Enter Quiz Code";
        return false;
    }
}