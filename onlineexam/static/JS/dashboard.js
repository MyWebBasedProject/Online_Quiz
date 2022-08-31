function buttonClicked(url, data){
    $.ajax({
        url: url, // /storeClassId
        type: "POST",
        data: {'data': data},
    
    })
}

var id;
function deleteButton(data){
    id  = data;
    displayForm();
}

function displayForm(){
    $("#delete-form").attr("style","display:block;");
    $("#delete-msg").text = "Do You want to leave/delete?";
}


function deleteTeacherClassroom(url){
    $.ajax({
        url: url,
        type: "POST",
        data:{'data':id},
        success:function(){
            window.location.reload();
            $("#delete-msg").text = "Record Deleted Successfully";
            $("#delete-form").attr("style", "display: none;");    
 
       }
    });
}

function deleteTeacherQuiz(url){
    $.ajax({
        url: url,
        type: "POST",
        data:{'data': id},
        success:function(){
            window.location.reload();
            $("#delete-msg").text = "Record Deleted Successfully";
            $("#delete-form").attr("style", "display: none;");    
        }
    });    
}

//Student YES button form
function deleteStudentClassroom(url)
{
    $.ajax({
        url: url,
        type: "POST",
        data:{'data':id},
        success:function(){
            window.location.reload();
            $("#delete-msg").text = "Record Deleted Successfully";
            $("#delete-form").attr("style", "display: none;");    
        }
    });
}

function popitup(url) {
    newwindow = window.open(url, 'name', 'height=11000,width=11000');
    if (window.focus) {
        newwindow.focus()
    }
    return false;
}