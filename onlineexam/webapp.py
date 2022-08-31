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
        img_name = str(count) + ".png"

        path = "static/Exam Proctor/register_id_" + str(session['teacher_id']) + "/class_id_" + str(
            session['class_id']) + "/quiz_id_" + str(session['quiz_id']) + "/student_" + str(session['id']) + "/Switched_Application/"
        img.save('onlineexam/' + path + img_name)
        violationTime = 1
        table = session['class_id'] + "_" + session['quiz_id']+'_report'
        msg = "Switched_Application"

        sql_query = f'INSERT INTO `{table}`(student_id, error_msg, image_path, violation_time) VALUES (%s, %s, %s, %s)'
        data = [session['id'], msg, path+img_name, violationTime]

        quiz.CUID_SQL(sql_query, data)
        return "1"


@app.route("/show_records_and_images", methods=['POST'])
def printAllRecords():
    if request.method == "POST":
        message = request.form['option']
        records_images_tuple = viewReport.getViolationAndImage(message)

        records = {}
        i = 0
        for record in records_images_tuple:
            records[i] = (record)
            i += 1

        # print(records)
        return records


@app.route("/proctor_report", methods=["POST"])
def view_report_template():
    if request.method == "POST":
        session["report_student_id"] = request.form["Proctor Report"]
        # print(f'webapp:  {session["report_student_id"]}')
        return render_template("proctor_report.html")


@app.route("/calculate_score", methods=["POST", "GET"])
def calculate_score():
    if request.method == "POST":
        quiz_code = session['quiz_id']
        marks = 0
        student_id = str(session['student_exam_id'])
        sql_query = f"SELECT duration FROM quiz_details WHERE quiz_id = %s"
        data = [quiz_code]
        myCursor = mydb.connection.cursor()
        myCursor.execute(sql_query, data)
        duration = myCursor.fetchone()
        # print(duration)
        total_time = duration['duration'] * 60 * 60

        time_in_seconds = viewReport.getViolationCount()
        violated_time = 0

        # print(time_in_seconds)
        for i in time_in_seconds:
            violated_time += i['violation_time']

        trust_score = 100 - (violated_time/total_time)*100

        # sql_query = f'SELECT answer, %s from`{quiz_code}`'
        # data = [student_id]
        # myCursor.execute(sql_query, data)
        # details = myCursor.fetchall()
        # table = "%s_result" % (quiz_code)
        # sql_query = f'SELECT %s from`{quiz_code}` where %s IS NOT NULL'
        # data = [student_id, student_id]
        # myCursor.execute(sql_query, data)
        # n = int(myCursor.rowcount)
        # if n < 0:
        #     sql_query = f'INSERT INTO `{table}`(student_id, marks, trust_score, result) VALUES (%s, "0", "0", "FAIL")'
        #     data = [student_id]
        #     myCursor.execute(sql_query, data)
        #     mydb.connection.commit()
        # elif details[i]['student_id'] == details[i]['answer']:
        #     marks += 1
        # score = (marks/n)*100
        trust = str(trust_score)
        # marks = str(marks)
        # table = quiz_code+"_results"
        # if score < 35 or trust_score < 90:
        #     sql_query = f'INSERT INTO `{table}`(student_id, marks, trust_score, result) VALUES (%s, %s, %s, "FAIL")'
        #     data = [student_id, marks, trust]
        #     myCursor.execute(sql_query, data)
        #     mydb.connection.commit()
        # else:
        #     sql_query = f'INSERT INTO `{table}`(student_id, marks, trust_score, result) VALUES (%s, %s, %s, "PASS")'
        #     data = [student_id, marks, trust]
        #     myCursor.execute(sql_query, data)
        #     mydb.connection.commit()
        # myCursor.close()
        return trust
