get_details();
function get_details() 
{
    $.ajax({
        url: '/getStudentExamQuestionDetails',
        method: "GET",
        success: function(questions){
            let length = Object.keys(questions).length;
            for(let i=0; i<length; i++)
            {

                $(".exam-result-body").append("\
                <div class='question-result' id="+ (i+1) +">\
                    <div class='question'>\
                        <h4>Question:"+ questions[i]['question'] +" </h4>\
                    </div>\
                    <div class='img-container'>\
                        <img src='' alt=''>\
                    </div>\
                    <div class='option-set'>\
                        <label for='"+ (i+1) +"_option_1'>\
                            <div class='option 1'>\
                                <input type='radio' onchange = changeColor('"+(i+1)+"_option_') name= '" + (i+1) + "_option' id='"+ (i+1) +"_option_1' value='1'>\
                                <h5>1: "+ questions[i]['option_1'] +"</h5>\
                            </div>\
                        </label>\
                        <label for='"+ (i+1) +"_option_2'>\
                            <div class='option 2'>\
                                <input type='radio' onchange= changeColor('"+ (i+1)+ "_option_') name= '" + (i+1) + "_option' id='"+ (i+1) +"_option_2' value='2'>\
                            <h5>2: "+ questions[i]['option_2'] +"</h5>\
                        </div>\
                        </label>\
                        \
                        <label for='"+ (i+1) +"_option_3'>\
                            <div class='option 3'>\
                                <input type='radio' onchange= changeColor('"+ (i+1)+"_option_') name= '" + (i+1) + "_option' id='"+ (i+1) +"_option_3' value='3'>\
                                <h5>3: "+ questions[i]['option_3'] +" </h5>\
                        </div>\
                        </label>\
                        <label for='"+ (i+1) +"_option_4'>\
                            <div class='option 4'>\
                            <input type='radio' onchange= changeColor('"+ (i+1)+"_option_') name= '" + (i+1) + "_option' id='"+ (i+1) +"_option_4' value='4'>\
                                <h5>4: "+ questions[i]['option_4'] +"</h5>\
                            </div>\
                        </label>\
                    </div>\
                </div>")
                

                if(questions[i]['question_img'] != "")
                {
                    $(".img-container").children("img").attr("src","http://127.0.0.1:5000/"+questions[i]['question_img']);
                    $(".img-container").children("img").attr("style","margin: 0 auto; display: block; max-height: 300px;");
                }
            }
        }
    });
}

function changeColor(name){

    for(let i=1; i<=4; i++)
    {
        if($("input[id='"+name+i+"']:checked").length == 1)
        {
            $("label[for='"+ name + i+"']").children(".option").attr("style","border: 2px solid green;background-color: rgb(215, 255, 215);")
        }
        else
        {
            $("label[for='"+ name+i+"']").children(".option").attr("style","border: 1px solid rgb(194, 194, 194);background-color: white;")
        }
    }

}
