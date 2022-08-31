var count = 0;
var socket;
var seconds = 0;
var screenChanged = 0;
var clickedSubmit = false;

socket = io.connect('http://127.0.0.1:5000/')
socket.emit('violation');


$(document).ready(function(){

    function takeScreenShot()
    {

        $.ajax({
            url: "/take_screenShot",
            type: "POST",
            data: {'count': count}
        
        });
    }

    document.addEventListener('visibilitychange', function(e) {
        if(document.visibilityState === "hidden")
        {
            takeScreenShot();
            ++screenChanged;
            if(screenChanged>10000)
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
            if(seconds >= 10000000)
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
        //    document.getElementById("mobile").innerHTML = "Number of Mobiles: " + mobile;
        //    document.getElementById("person").innerHTML = "Number of Persons: " + person;
        //    document.getElementById("correct_person").innerHTML = "Correct Person: " + correct_person;
    });



    socket.on('violation',function(faces, eye, face_orinetation){
        // document.getElementById("faces").innerHTML = "Number of Faces: " + faces;
        //document.getElementById("face_oreintation").innerHTML = "Face Oreintation: " + face_orinetation;
        //document.getElementById("eye").innerHTML = "Eye Direction: " + eye;
    });

    socket.on('number_of_violation', function(no_violation){
        //document.getElementById("violation").innerHTML = "Number  Of Violations Performed: " + no_violation;
    });

    socket.on('face_distance', function(face_perimeter){
        // console.log(face_perimeter);
        
    });

});

function closeCamera()
        {
                $.ajax({
                    url: "/camera_close",
                    type: "POST",
                    timeout:3000
                });
        }

window.onbeforeunload=()=>
    {
        socket.disconnect();
        closeCamera();
    }