function retriveQuestion(question_id, total_count, operation){

    question_id = parseInt(question_id);
    total_count = parseInt(total_count);

    if(operation=='plus')
    {
        if(question_id == total_count)
        {
            question_id = 1;
        }
        else
            question_id++;   
    }
    else 
    {
        if(question_id == 1)
            question_id = total_count;
        else
            question_id--;  
    }

    retriveOperation(question_id, total_count);

}

function retriveOperation(question_id, total_count){
    $.ajax({
        url: "/retriveQuestion",
        type: "POST",
        data: {'question_id': question_id},
        success: function(question_details){
            
            $("#question_text").val(question_details['question']);
            console.log($("#question_text").val())
            // console.log(question_details['option_1']);
            $("#option_1").val(question_details['option_1']);
            $("#option_2").val(question_details['option_2']);
            $("#option_3").val(question_details['option_3']);
            $("#option_4").val(question_details['option_4']);
            $("#answer").val(question_details['answer']);

            $("#back-button").attr("onclick", "retriveQuestion('" + question_id + "','" + total_count + "','minus')");
            $("#next-button").attr("onclick", "retriveQuestion('" + question_id + "','" + total_count + "','plus')");
            $("#current-total").text( question_id + "/" + total_count);
            $('#set-question').attr("onclick", "teacherSetQuestion('" + question_id + "')");
            $('#img-preview').attr("src", "/" + question_details['question_img']);
        }
    });
}


function teacherSetQuestion(question_id){

    let question = document.getElementById("question_text").value;
    let option_1 = document.getElementById("option_1").value;
    let option_2 = document.getElementById("option_2").value;
    let option_3 = document.getElementById("option_3").value;
    let option_4 = document.getElementById("option_4").value;
    let answer = document.getElementById("answer").value;

    $.ajax({
        url:"/teacher/setQuestion",
        type: "POST",
        data: {'question':question, 'option_1':option_1,'option_2':option_2,'option_3':option_3,'option_4':option_4, 'answer':answer, 'question_id': question_id},
        success:function(){
            // window.location.reload();
            
        }
    });
}


function uploadQuestionImage(event){  
    let question_image_path = document.getElementById("question_image").value;
    let question_id = $("#current-total").html()[0];
    const image_arr = new Array("png", "jpeg", "jpg");
    let extensions = question_image_path.split('.').pop();
    let contains = false;
    for(let i=0; i<3; i++)
    {
        if(extensions == image_arr[i]){
            contains = true;
        }
    }
      
    if(event.target.files.length == 1){
       
        var src = URL.createObjectURL(event.target.files[0]);
        console.log(src);
        console.log(event.target.files[0]);
        var myImage = $("#img-preview");
        myImage.attr("src", src);
        myImage.attr("style", "display: block; height: 100%; margin: 0 auto;");
        
    }

    if(contains)
    {
        question_id = parseInt(question_id);

        let formData = new FormData();
        formData.append('source', event.target.files[0], 'image_file');
        formData.append('question_id', question_id);

        $.ajax({
            url: "/teacher/uploadQuestionImage",
            type:"POST",
            data: formData,
            processData: false,
            contentType: false,
            success: (image_path)=>{
                
                
                $('#img-preview').attr("src", "http://127.0.0.1:5000/"+image_path)

                document.getElementById("upload-image-label").innerHTML = "Image Uploaded Successfully. Upload again?";
                document.getElementById("upload-image-label").style = "background-color: white; color:blue; border:2px solid blue;";

            }
        });  

    }
}
