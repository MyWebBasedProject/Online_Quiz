var count = 0;

    function showViewButton()
    {
        $("#viewExamButton").show();
        $("#endExamButton").hide();
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

        var socket = io.connect('http://127.0.0.1:5000/')

        console.log(socket);

        document.addEventListener('visibilitychange', function(e) {
            if(document.visibilityState === "hidden")
            {
                console.log(document.hasFocus());
                takeScreenShot();
                count = count + 1;
                //document.getElementById("canSee").innerHTML = "Number of times application switched: " + count;

            }
        });

        socket.on('detect_person_mobile',function(person, mobile, correct_person){
           //document.getElementById("mobile").innerHTML = "Number of Mobiles: " + mobile;
           //document.getElementById("person").innerHTML = "Number of Persons: " + person;
           //document.getElementById("correct_person").innerHTML = "Correct Person: " + correct_person;
        });



        socket.on('violation',function(faces, eye, face_orinetation){
            //document.getElementById("faces").innerHTML = "Number of Faces: " + faces;
            //document.getElementById("face_oreintation").innerHTML = "Face Oreintation: " + face_orinetation;
            //document.getElementById("eye").innerHTML = "Eye Direction: " + eye;
        });

        socket.on('number_of_violation', function(no_violation){
            //document.getElementById("violation").innerHTML = "Number  Of Violations Performed: " + no_violation;
        });

        $("#startButton").on('click',function(){
            socket.emit('violation');
        });

        $('#endExamButton').on('click',function(){
            socket.emit('close_camera');
            showViewButton();
        });

    });