from flask import render_template, request, session
from onlineexam import app, viewReport, mydb, quiz
import pyautogui
import time


@app.route("/take_screenShot", methods=['POST'])
def takeScreenShot():
    if request.method == "POST":
        count = request.form['count']
        time.sleep(0.15)
        img = pyautogui.screenshot()
        myCursor = mydb.connection.cursor()
        img_name = str(count) + ".png"

        path = "static/" + session['code'] + "/"+ session['email'] +  "/Switched_Application/"
        img.save('onlineexam/' + path + img_name)
        violationTime = 1
        table = session['code']+'_report'
        sql_query = f'INSERT INTO `{table}`(message, screenshot, violationTime) VALUES (Switched_Application, %s, %s)'
        data = [path, violationTime]
        myCursor.execute(sql_query, data)
        mydb.connection.commit()
        myCursor.close()
        return "1"


@app.route("/show_records_and_images", methods=['POST'])
def printAllRecords():
    if request.method == "POST":
        message = request.form['option']
        #print(message)
        records_images_tuple = viewReport.getViolationAndImage(message)
        record_images = {}
        for i in records_images_tuple:
            record_images[i[0]] = {
                "message": i[2],
                "image": str(i[3]),
                "duration": str(i[4])
            }

        return record_images


@app.route('/')
def home():
    return render_template('HomePage.html')


@app.route("/face_detect", methods=["POST"])
def faceDetect():
    if request.method == "POST":
        return render_template("face_detect.html")


@app.route("/proctor_report", methods=["POST"])
def view_report_template():
    if request.method == "POST":
        session["report_student_id"] = request.form["Proctor Report"]
        return render_template("proctor_report.html")

@app.route("/calculate_score", methods=["POST"])
def calculate_score():
    if request.method == "POST":
        quiz_code = session['report_code']
        sql_query = f"SELECT duration,questions FROM quiz_details WHERE code= %s"
        data=[quiz_code]
        myCursor = mydb.connection.cursor()
        myCursor.execute(sql_query, data)
        mydb.connection.commit()
        duration = myCursor.fetchone()
        total_time = duration[0].seconds
        n = int(duration[1])
        time_in_seconds = viewReport.getViolationCount()

        violated_time = 0
        print(time_in_seconds)
        for i in time_in_seconds:
            violated_time += i[0]

        null = 0
        marks = 0
        result = " "
        trust_score = (violated_time/total_time)*100
        trust_score = 100 - trust_score
        id = session['student_id']
        sql_query = f"SELECT answer,%s FROM `{session['code']}`"
        data=[quiz_code]
        myCursor.execute(sql_query, data)
        mydb.connection.commit()
        answer = myCursor.fetchall()
        for i in range (1,n+1):
            if answer[i]['id'] == "NULL":
                null+=1
            elif answer[i]['answer'] == answer[i]['id']:
                marks += 1
        percent = (marks/n)*100
        if null == n:
            result == "FAIL"
        if percent < 50 or trust_score < 90:
            result = "FAIL"
        else:
            result = "PASS"
        table = session['code']+'_answer'
        trust_score = str(trust_score)
        marks = str(marks)
        sql_query = f"INSERT INTO `{table}` (student_id, exam_result, trust_score, result) VALUES (%s, %s, %s, %s)"
        data=[quiz_code,marks,trust_score,result]
        myCursor.execute(sql_query, data)
        mydb.connection.commit()