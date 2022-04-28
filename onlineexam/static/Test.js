    var count = 0;
    var socket;
    
    showQuestions();

    //console.log("Show Questions");
    function showQuestions()
    {
        $(".questions").children().remove();
        $.ajax({
            url: "/get_questions",
            type: "POST",
            success: function(data)
            {
            var num = 1;
                for(var key in data)
                {
                    
                    if (data[key]['image'] === "NULL"){
                        data[key]['image'] = " "
                    }
                    $(".questions").append("<br><p>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp Q. " + data[key]['question']
                    + "</p> <br><br>&nbsp&nbsp&nbsp&nbsp<p>"+ data[key]['image']
                    +"</p><br><br>&nbsp&nbsp&nbsp&nbsp<input type=\"radio\" name=\"question_" + num + "\" value=" + 1
                    + "><label for=\"option1\">" +  data[key]['option_1'] + "</label><br><br>"
                    + "<br> &nbsp&nbsp&nbsp&nbsp   <input type=\"radio\"  name=\"question_" + num + "\" value=" + 2
                    + "><label for=\"option2\">" +  data[key]['option_2'] + "</label><br><br>"
                    + "<br> &nbsp&nbsp&nbsp&nbsp <input type=\"radio\" name=\"question_" + num + "\" value=" + 3
                    + "><label for=\"option3\">" +  data[key]['option_3'] + "</label><br><br>"
                    + "<br> &nbsp&nbsp&nbsp&nbsp <input type=\"radio\" name=\"question_" + num + "\" value=" + 4
                    + "><label for=\"option4\">" +  data[key]['option_4'] + "</label> "
                    +"<br><br><hr style=width:98%;text-align:center;margin-left:1%></hr>" );
                }
            }


        });
    }

    var clickedSubmit = false;
    function closeCamera()
        {
                $.ajax({
                    url: "/camera_close",
                    type: "POST",
                    timeout:3000
                });
        }


    window.onbeforeunload = function(event){
        socket.disconnect();
        closeCamera();
    }
$(document).ready(function(){

    function takeScreenShot()
    {

        $.ajax({
            url: "/take_screenShot",
            type: "POST",
            data: {'count': count},
            success: function(data)
            {

            }
        });
    }



    socket = io.connect('http://127.0.0.1:5000/')
    console.log(socket);
    socket.emit('violation');

    document.addEventListener('visibilitychange', function(e) {
        if(document.visibilityState === "hidden")
        {
            takeScreenShot();
            ++screenChanged;
            if(screenChanged>1)
            {

                closeCamera();
                setTimeout(function(){window.close()}, 3000);

            }
            setInterval(incrementSeconds, 1000);
            count = count + 1;
        }
        else
        {
            clearInterval(incrementSeconds, 1000);
            if(seconds >= 3)
            {
                closeCamera();
                setTimeout(function(){window.close()}, 3000);

            }
            seconds = 0;
        }
    });

function incrementSeconds() {
    seconds += 1;
}



    socket.on('detect_person_mobile',function(person, mobile, correct_person){
//           document.getElementById("mobile").innerHTML = "Number of Mobiles: " + mobile;
//           document.getElementById("person").innerHTML = "Number of Persons: " + person;
//           document.getElementById("correct_person").innerHTML = "Correct Person: " + correct_person;
    });



    socket.on('violation',function(faces, eye, face_orinetation){
        //document.getElementById("faces").innerHTML = "Number of Faces: " + faces;
        //document.getElementById("face_oreintation").innerHTML = "Face Oreintation: " + face_orinetation;
        //document.getElementById("eye").innerHTML = "Eye Direction: " + eye;
    });

    socket.on('number_of_violation', function(no_violation){
        //document.getElementById("violation").innerHTML = "Number  Of Violations Performed: " + no_violation;
    });

    socket.on('face_distance', function(face_perimeter){

    });

});