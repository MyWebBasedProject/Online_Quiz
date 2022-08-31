# from crypt import methods
from array import array
# from crypt import methods
from genericpath import isdir
import os
import profile
from flask import render_template, request, redirect, url_for, session
# from flask_mail import Message
from flask_mysqldb import MySQLdb
from onlineexam import app, mydb
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import random
import json
import time
import string
import cv2
import face_recognition
from PIL import Image
import io
import urllib.request
from datetime import datetime, timedelta


# region Session

'''
session[id] --> teacher's / student's ID
session[class_id]
session[quiz_id]
'''

# endregion


# region Variables
teacher_id = ""
student_id = ""
class_id = ""
quiz_id = ""
profile_pic = ""
# endregion

# region CRUD Operations


def CUID_SQL(sql_query, data=[]):
    myCursor = mydb.connection.cursor()
    myCursor.execute(sql_query, data)
    myCursor.connection.commit()
    myCursor.close()


def SelectSQL(sql_query, data=[]):
    myCursor = mydb.connection.cursor()
    myCursor.execute(sql_query, data)
    queryDetails = {}
    queryDetails['rows'] = myCursor.fetchall()
    queryDetails['row_count'] = myCursor.rowcount
    myCursor.close()
    return queryDetails

# endregion

# region Teachers Functions


@app.route('/teacher/teacher/<username>', methods=['GET', 'POST'])
def teacher(username):
    id = session['id']
    profilepic = session['profile_pic']
    date = datetime.date(datetime.now())

    sql_query = f"SELECT * FROM classroom WHERE teacher_id = %s"
    data = [id]
    query_results = SelectSQL(sql_query, data)

    return render_template("teacher/teacher.html", username=username, details=profilepic, data=query_results['rows'], n=query_results['row_count'])


@app.route('/teacher/teacher/<username>/createClassroom', methods=['GET', 'POST'])
def createClassroom(username):
    profilepic = session['profile_pic']
    if request.method == 'POST':
        subject = request.form['subject']
        branch = request.form['branch']
        grad_yr = request.form['grad_yr']
        semester = request.form['semester']
        class_id = ''.join(random.choices(
            string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits, k=7))

        sql_query = f"INSERT INTO classroom (class_id, subject_name, branch, grad_year, semester, teacher_id) VALUES (%s, %s, %s, %s, %s, %s)"
        data = [class_id, subject, branch, grad_yr, semester, session['id']]
        CUID_SQL(sql_query, data)

        os.mkdir('onlineexam/static/Question Images/register_id_' +
                 str(session['id']) + "/class_id_" + str(class_id))

        os.mkdir('onlineexam/static/Exam Proctor/register_id_' +
                 str(session['id']) + "/class_id_" + str(class_id))

        return redirect(url_for('teacher', username=username))

    return render_template('teacher/createClassroom.html', username=username, details=profilepic)


@app.route("/teacher/teacher/<username>/viewAllQuiz")
def currentClassroom(username):

    profilepic = session['profile_pic']
    sql_query = f"SELECT * FROM classroom WHERE class_id = %s"
    data = [session['class_id']]
    class_details = SelectSQL(sql_query, data)

    sql_query = f"SELECT * FROM quiz_details WHERE class_id = %s"
    quiz_details = SelectSQL(sql_query, data)

    exam_completed = []
    for quiz_detail in quiz_details['rows']:
        exam_end_time = quiz_detail['quiz_date_time'] + \
            timedelta(hours=quiz_detail['duration'])
        if quiz_detail['quiz_date_time'] + timedelta(hours=quiz_detail['duration']) < datetime.now():
            exam_completed.append(True)
        else:
            exam_completed.append(False)

    return render_template('teacher/viewAllQuiz.html',
                           username=username,
                           details=profilepic,
                           quiz_details=quiz_details['rows'],
                           class_details=class_details['rows'],
                           exam_completed=exam_completed,
                           quiz_details_count=quiz_details['row_count'])


@app.route("/storeClassId", methods=["POST", "GET"])
def storeClassId():
    if request.method == 'POST':
        session['class_id'] = request.form['data']
        return ""


@app.route('/teacher/teacher/<username>/createQuiz', methods=["POST", "GET"])
def createQuiz(username):
    profilepic = session['profile_pic']
    if request.method == "POST":

        sql_query = f"INSERT INTO quiz_details (class_id, no_of_questions, quiz_date_time, duration, quiz_title) VALUES (%s, %s, %s, %s, %s)"
        data = [session['class_id'], int(request.form['no_question']), request.form['exam_date_time'],
                request.form['exam_duration'], request.form['quiz_title']]
        CUID_SQL(sql_query, data)

        sql_query = f"(SELECT max(`quiz_id`) FROM quiz_details)"
        query_details = SelectSQL(sql_query)

        sql_query = f"CREATE TABLE IF NOT EXISTS `{session['class_id']}_{query_details['rows'][0]['max(`quiz_id`)']}_report`(report_id int AUTO_INCREMENT PRIMARY KEY,student_id int, error_msg varchar(20), image_path varchar(100), violation_time int)  "
        CUID_SQL(sql_query)

        sql_query = f"CREATE TABLE `{session['class_id']}_{query_details['rows'][0]['max(`quiz_id`)']}` (question_id INT AUTO_INCREMENT PRIMARY KEY, question varchar(1000), question_img varchar(250), option_1 varchar(250), option_2 varchar(250), option_3 varchar(250), option_4 varchar(250), answer int)"
        CUID_SQL(sql_query)

        sql_query = f"CREATE TABLE `{session['class_id']}_{query_details['rows'][0]['max(`quiz_id`)']}_exam_report` (question_id int not null primary key )"
        CUID_SQL(sql_query)

        sql_query = f"ALTER TABLE quiz_details AUTO_INCREMENT = {query_details['rows'][0]['max(`quiz_id`)']}"
        CUID_SQL(sql_query)

        for i in range(0, int(request.form['no_question'])):
            sql_query = f"INSERT INTO `{session['class_id']}_{query_details['rows'][0]['max(`quiz_id`)']}` (question, question_img , option_1 , option_2 , option_3 , option_4 , answer) VALUES (%s, %s, %s,%s, %s, %s,%s)"
            data = ["", "", "", "", "", "", 0]
            CUID_SQL(sql_query, data)

            sql_query = f"INSERT INTO `{session['class_id']}_{query_details['rows'][0]['max(`quiz_id`)']}_exam_report` (question_id) VALUES (%s)"
            CUID_SQL(sql_query, [i+1])

            path = 'onlineexam/static/Question Images/register_id_' + str(session['id']) + "/class_id_" + str(
                session['class_id']) + "/quiz_id_" + str(query_details['rows'][0]['max(`quiz_id`)'])

            if os.path.isdir(path) != False:
                os.mkdir('onlineexam/static/Question Images/register_id_' +
                         str(session['id']) + "/class_id_" + str(session['class_id']) + "/quiz_id_" + str(query_details['rows'][0]['max(`quiz_id`)']))

                os.mkdir('onlineexam/static/Exam Proctor/register_id_' +
                         str(session['id']) + "/class_id_" + str(session['class_id']) + "/quiz_id_" + str(query_details['rows'][0]['max(`quiz_id`)']))

        return redirect(url_for('currentClassroom', username=username))
    return render_template('teacher/createQuiz.html', username=username, details=profilepic)


@app.route('/teacher/teacher/<username>/viewSingleQuiz')
def viewTeacherSingleQuiz(username):
    sql_query = f"SELECT * FROM `{session['class_id']}_{session['quiz_id']}`"
    quiz_question_details = SelectSQL(sql_query)
    session['total_count'] = quiz_question_details['row_count']

    return render_template("teacher/viewSingleQuiz.html", username=username, details=session['profile_pic'], quiz_question_details=quiz_question_details['rows'], total_count=quiz_question_details['row_count'])


@app.route("/storeQuizId", methods=["POST", "GET"])
def storeQuizId():
    if request.method == 'POST':
        session['quiz_id'] = request.form['data']
        return ""


@app.route("/retriveQuestion", methods=["POST", "GET"])
def retriveQuestion():
    if request.method == 'POST':
        question_id = request.form['question_id']
        sql_query = f"SELECT * FROM `{session['class_id']}_{session['quiz_id']}` WHERE question_id=%s LIMIT 1"
        data = [question_id]
        question_details = SelectSQL(sql_query, data)
        return question_details['rows'][0]


@app.route("/teacher/setQuestion", methods=["POST", "GET"])
def teacherSetQuestion():
    if request.method == "POST":
        question_id = request.form['question_id']
        sql_query = f"UPDATE `{session['class_id']}_{session['quiz_id']}` SET question=%s, question_img=%s, option_1 = %s, option_2 = %s, option_3 = %s, option_4 = %s, answer = %s WHERE question_id = %s"

        data = [request.form['question'], request.form['question_img'], request.form['option_1'], request.form['option_2'],
                request.form['option_3'], request.form['option_4'], request.form['answer'], question_id]
        CUID_SQL(sql_query, data)
        return ""


@app.route('/deleteTeacherClassroom', methods=['POST', 'GET'])
def deleteTeacherContent():
    if request.method == "POST":
        class_id = request.form['data']

        sql_query = f"DELETE FROM classroom WHERE class_id = %s AND teacher_id = %s"
        data = [class_id, session['id']]
        CUID_SQL(sql_query, data)

        return ""


@app.route('/deleteTeacherQuiz', methods=['POST', 'GET'])
def deleteTeacherQuiz():
    if request.method == "POST":
        quiz_id = request.form['data']
        # print(quiz_id)

        sql_query = f"DELETE FROM quiz_details WHERE quiz_id = %s AND class_id = %s"
        data = [quiz_id, session['class_id']]
        CUID_SQL(sql_query, data)

        sql_query = f"DROP TABLE `{session['class_id']}_{quiz_id}`"
        CUID_SQL(sql_query)

        sql_query = f"DROP TABLE `{session['class_id']}_{quiz_id}_exam_report`"
        CUID_SQL(sql_query)

        sql_query = f"DROP TABLE `{session['class_id']}_{quiz_id}_report`"
        CUID_SQL(sql_query)

        return ""


@app.route("/teacher/uploadQuestionImage", methods=["POST", "GET"])
def uploadQuestionImage():
    if request.method == "POST":
        question_id = request.form['question_id']
        profile_pic = request.files.get('source')
        filename = str(question_id) + ".png"
        parent_path = 'onlineexam/'
        static_path = 'static/Question Images/register_id_' + str(session['id']) + "/class_id_" + str(
            session['class_id']) + "/quiz_id_" + str(session['quiz_id']) + filename
        path = os.path.join(parent_path, static_path)
        profile_pic.save(path)
        sql_query = f"UPDATE `{str(session['class_id'])}_{str(session['quiz_id'])}` SET question_img = %s  WHERE question_id = %s"
        data = [static_path, question_id]
        CUID_SQL(sql_query, data)

        return static_path


@app.route("/teacher/teacher/<username>/examReport", methods=['POST', 'GET'])
def examReport(username):

    sql_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s AND COLUMN_NAME != 'question_id' "
    table = str(session['class_id']) + "_" + \
        str(session['quiz_id'])+"_exam_report"
    data = [table]
    query_details = SelectSQL(sql_query, data)

    student_details = []
    for query_detail in query_details['rows']:
        # print(query_detail)
        id = int(query_detail['COLUMN_NAME'])
        sql_query = f"SELECT * FROM student WHERE id = %s"
        student_details.append(SelectSQL(sql_query, [id])['rows'][0])

    # for id in student_ids:

    return render_template("teacher/examReport.html", username=username, student_details=student_details, details=session['profile_pic'])

# endregion


# region Functions Related To Students

@app.route('/student/student/<username>', methods=['GET', 'POST'])
def student(username):
    profilepic = session['profile_pic']
    sql_query = f"SELECT class_joined FROM student WHERE id=%s"
    data = [session['id']]
    query_details = SelectSQL(sql_query, data)
    class_list = query_details['rows'][0]

    class_dict_list = json.loads(class_list["class_joined"])
    class_list = class_dict_list["class_joined"]

    classroom = []
    for class_id in class_list:
        sql_query = f"SELECT * FROM classroom WHERE class_id = %s"
        data = [class_id]
        query_details = SelectSQL(sql_query, data)
        if query_details['row_count'] > 0:
            classroom.append(query_details['rows'][0])

    # print(classroom)

    return render_template("student/student.html", username=username, details=profilepic, classroom=classroom)


@app.route('/student/student/<username>/joinClassroom', methods=['GET', 'POST'])
def joinClassroom(username):
    profilepic = session['profile_pic']
    if request.method == "POST":
        class_id = request.form['class_id']
        sql_query = f"SELECT * FROM classroom WHERE class_id=%s"
        data = [class_id]
        query_details = SelectSQL(sql_query, data)

        if query_details['row_count'] == 1:
            sql_query = f"SELECT * FROM student WHERE id = %s"
            data = [session['id']]
            query_details = SelectSQL(sql_query, data)

            json_data = json.loads(query_details['rows'][0]['class_joined'])

            class_list = json_data["class_joined"]

            if class_list.count(class_id) == 0:
                json_data["class_joined"].append(class_id)
                sql_query = f"UPDATE student SET class_joined=%s WHERE id = %s"
                json_data = json.dumps(json_data)
                data = [json_data, session['id']]
                CUID_SQL(sql_query, data)
                msg = "Joined Class Successfully"
            elif class_list.count(class_id) == 1:
                msg = "Class already joined"
        else:
            msg = "Wrong class code"

        return render_template("student/joinClassroom.html", username=username, details=profilepic, form_submitted_validation=msg)

    return render_template("student/joinClassroom.html", username=username, details=profilepic, form_submitted_validation="")


@app.route('/student/student/<username>/viewAllQuiz')
def viewStudentAllQuiz(username):
    sql_query = f"SELECT * FROM classroom WHERE class_id=%s"
    data = [session['class_id']]

    quiz_details = SelectSQL(sql_query, data)

    session['teacher_id'] = quiz_details['rows'][0]['teacher_id']
    sql_query = f"SELECT * FROM quiz_details WHERE class_id = %s AND (SELECT DATE_ADD(quiz_date_time, interval duration hour)) > (SELECT NOW())"
    data = [session['class_id']]
    quiz_details = SelectSQL(sql_query, data)

    exam_started = []
    for quiz in quiz_details['rows']:
        exam_time = quiz['quiz_date_time']
        exam_duration = quiz['duration']
        current_time = datetime.now()

        exam_end_time = exam_time + timedelta(hours=exam_duration)
        exam_started.append(
            exam_end_time > current_time and exam_time <= current_time)
        # print()

    # print(quiz_details['rows'].count())
    return render_template("student/viewAllQuiz.html", username=username, details=session['profile_pic'], quiz_details=quiz_details['rows'], exam_started=exam_started, row_count=quiz_details['row_count'])


@app.route('/deleteStudentClassroom', methods=['POST', 'GET'])
def deleteStudentContent():
    if request.method == "POST":
        class_id = request.form['data']
        sql_query = f"SELECT * FROM student WHERE id=%s"
        data = [session['id']]
        query_details = SelectSQL(sql_query, data)
        class_joined = json.loads(query_details['rows'][0]['class_joined'])
        class_joined['class_joined'].remove(class_id)
        class_joined = json.dumps(class_joined)
        sql_query = f"UPDATE student SET class_joined = %s WHERE id = %s"
        data = [class_joined, session['id']]
        CUID_SQL(sql_query, data)
        return ""


@app.route('/student/examPage', methods=['GET'])
def studentExamPage():
    global class_id, quiz_id, student_id, teacher_id, profile_pic
    class_id = session['class_id']
    quiz_id = session['quiz_id']
    student_id = session['id']
    teacher_id = session['teacher_id']
    profile_pic = session['profile_pic']
    createFoldersForViolations()

    sql_query = f"SELECT * FROM information_schema.columns WHERE TABLE_NAME = %s AND COLUMN_NAME =%s "
    exam_report_table = session['class_id'] + \
        "_" + str(session['quiz_id']) + "_exam_report"
    data = [exam_report_table, session['id']]
    query_details = SelectSQL(sql_query, data)
    # print("count rows :" + str(query_details['row_count']))

    if query_details['row_count'] == 0:
        sql_query = f"ALTER TABLE `{exam_report_table}`  ADD COLUMN (`{str(session['id'])}` int DEFAULT 0)"
        CUID_SQL(sql_query)

    return render_template("student/examPage.html")


@app.route('/getStudentExamQuestionDetails')
def getStudentExamQuestionDetails():
    sql_query = f"SELECT * FROM `{session['class_id']}_{session['quiz_id']}`"
    query_details = SelectSQL(sql_query)
    query_details = query_details['rows']
    question_details = {}
    i = 0
    for detail in query_details:
        question_details[i] = detail
        i += 1

    return question_details


@app.route("/student/examSubmitted.html", methods=["GET"])
def examSubmitted():
    return render_template("student/examSubmitted.html")


@app.route("/getStudentExamResults", methods=["GET", "POST"])
def getStudentExamResults():
    if request.method == "POST":
        for i in range(0, len(request.form)):
            sql_query = f"UPDATE `{session['class_id']}_{session['quiz_id']}_exam_report` SET `%s` = %s WHERE `question_id` = %s"
            data = [session['id'], int(request.form[str(i+1)+'_option']), i+1]
            # print(sql_query)
            CUID_SQL(sql_query, data)

        return redirect(url_for("examSubmitted"))
    # endregion

# region Default and Logout


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# endregion

# region Login Related Functions


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'category' in request.form:
        email = request.form['email']
        password = request.form['password']
        category = request.form['category']

        cursor = mydb.connection.cursor()
        cursor.execute('SELECT * FROM ' + category +
                       ' WHERE email = % s ', (email, ))
        account = cursor.fetchone()
        if account:
            cursor.execute('SELECT * FROM ' + category +
                           ' WHERE email = % s AND password = % s', (email, password, ))
            pwd = cursor.fetchone()
            if pwd:
                session['username'] = pwd['first_name']
                session['loggedin'] = True
                session['profile_pic'] = pwd['profile_pic']

                session['email'] = pwd['email']
                session['id'] = pwd['id']

                if category == 'student':
                    session['branch'] = pwd['branch']
                    session['semester'] = pwd['semester']

                    return redirect(url_for('student', username=pwd['first_name']))
                else:
                    return redirect(url_for('teacher', username=pwd['first_name']))
            else:
                msg = 'Invalid Password'
                return render_template('login.html', msg=msg)
        else:
            msg = 'Register first!'
            return render_template('login.html', msg=msg)
    return render_template('login.html', msg=msg)
# endregion


# region Registration Function Redirecting to Page

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/Register/TeacherSignUp', methods=['GET', 'POST'])
def TeacherSignUp():
    msg = ''
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        profile_pic = request.files['profile_pic']

        cursor = mydb.connection.cursor()
        cursor.execute(
            'SELECT * FROM teacher WHERE email = % s ', (email, ))
        account = cursor.fetchone()

        cursor.execute('select * from student')
        registration_id = cursor.rowcount + 1

        if account:
            msg = 'Account already exists !'
            return render_template('Register/TeacherSignUp.html', msg=msg)
        else:
            name = '%s%s%s_%s.%s' % (
                first_name, middle_name, last_name, registration_id, "png")
            name = name.replace(" ", "")
            filename = secure_filename(name)
            profile_pic.save(os.path.join(app.config['teacher'], filename))
            profile_pic = "http://127.0.0.1:5000/static/profilepics/teacher/%s" % (
                name)
            cursor.execute('INSERT INTO teacher VALUES (%s, %s, % s, % s, % s, % s, % s, % s)',
                           (registration_id, profile_pic, first_name, last_name, middle_name, dob, email, password, ))
            os.mkdir('onlineexam/static/Question Images/register_id_' +
                     str(registration_id))
            os.mkdir('onlineexam/static/Exam Proctor/register_id_' +
                     str(registration_id))

            mydb.connection.commit()
            msg = '%s %s, you have successfully registered ! Your Id is %s' % (
                first_name, last_name, registration_id)
            return redirect(url_for("home"))
    return render_template('Register/TeacherSignUp.html', msg=msg)


@app.route('/Register/StudentSignUp', methods=['GET', 'POST'])
def StudentSignUp():
    msg = ''
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        semester = request.form['semester']
        profile_pic = request.files['profile_pic']

        cursor = mydb.connection.cursor()
        cursor.execute('SELECT * FROM student WHERE email = % s ', (email, ))
        account = cursor.fetchone()
        cursor.execute('SELECT * from student')
        registration_id = cursor.rowcount + 1

        if account:
            msg = 'Account already exists !'
            return render_template('Register/StudentSignUp.html', msg=msg)
        else:
            name = '%s%s%s_%s.%s' % (
                first_name, middle_name, last_name, registration_id, "jpg")
            name = name.replace(" ", "")
            filename = secure_filename(name)
            profile_pic.save(os.path.join(app.config['student'], filename))
            profile_pic = "/static/profilepics/student/%s" % (
                name)
            sql_query = f"INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            data = [registration_id, profile_pic, first_name, last_name,
                    middle_name, dob, email, password, branch, semester, json.load('{"class"=[]}')]
            cursor.execute(sql_query, data)
            mydb.connection.commit()
            msg = '%s %s, you have successfully registered ! Your Id is %s' % (
                first_name, last_name, registration_id)
            return redirect(url_for("home"))

    return render_template('Register/StudentSignUp.html', msg=msg)

# endregion


# @app.route('/quiz_report', methods=['GET', 'POST'])
# def quiz_report():
#     if "report" in request.form:
#         code = request.form['report']
#         branch = request.form['branch']
#         sem = request.form['sem']
#         marks = " "
#         trust_score = " "
#         grade = " "
#         cursor = mydb.connection.cursor()
#         cursor.execute(
#             "SELECT * FROM student where branch = %s and semester = %s", (branch, sem, ))
#         n = n = cursor.rowcount
#         cursor.execute(
#             "SELECT * FROM student where branch = %s and semester = %s", (branch, sem, ))
#         details = cursor.fetchall()
#         for i in range(0, n):
#             if details:
#                 id = details[i]['id']
#                 cursor.execute("SELECT * FROM "+code +
#                                "_result where student_id=%s", (id,))
#                 result = cursor.fetchone()
#                 if result:
#                     marks = result['marks']
#                     trust_score = result['trust_score']
#                     grade = result['result']
#         session['report_code'] = code
#         session['code'] = code
#         return render_template("quiz_report.html", code=code, data=details, n=n, marks=marks, trust_score=trust_score, grade=grade)
#     return render_template("quiz_report.html")

@app.route('/teacher/teacher/<username>/examReport/examResults')
def showExamResults(username):
    return render_template("teacher/examResult.html",
                           username=username,
                           details=session['profile_pic'])


@app.route('/teacher/getExamResult')
def getExamResults():
    table = session['class_id'] + "_" + \
        str(session['quiz_id']) + "_exam_report"

    table_answer = session['class_id'] + "_" + str(session['quiz_id'])
    marks = 0

    sql_query = f"SELECT `{session['student_exam_id']}` FROM `{table}`"
    exam_response_details = SelectSQL(sql_query)

    sql_query = f"SELECT * FROM `{table_answer}`"
    correct_answer = SelectSQL(sql_query)

    for i in range(0, exam_response_details['row_count']):
        if exam_response_details['rows'][i][str(session['student_exam_id'])] == correct_answer['rows'][i]['answer'] and exam_response_details['rows'][i][str(session['student_exam_id'])] != 0:
            marks += 1

    data = {'marks_scored': marks,
            'total_questions': exam_response_details['row_count'],
            'response': exam_response_details['rows'],
            'correct_answer': correct_answer['rows'],
            'student_id': session['student_exam_id']}
    return data


@app.route("/teacher/teacher/<username>/examReport/proctoreReport")
def proctorResults(username):
    table = session['class_id'] + "_" + \
        str(session['quiz_id']) + "_report"

    sql_query = f"SELECT * FROM `{table}` WHERE student_id = %s"
    proctor_details = SelectSQL(sql_query, [session['student_exam_id']])
    # print(proctor_details)

    return render_template("teacher/proctorReport.html", username=username,
                           details=session['profile_pic'])


@app.route('/storeStudentId', methods=['GET', 'POST'])
def storeStudentExamID():
    if request.method == "POST":
        session['student_exam_id'] = request.form['id']
        # print(session['student_exam_id'])
        return ""


def createFoldersForViolations():

    folders = ["Face_Left_Side", "Face_Right_Side", "Looking_Left", "Looking_Right", "Mobile_Detected",
               "Multiple_Person_Detected", "No_Face_Detected", "Switched_Application", "Wrong_Person"]
    parent_dir = "onlineexam/static/"
    directory = "Exam Proctor/register_id_" + str(session['teacher_id']) + "/class_id_" + str(
        session['class_id']) + "/quiz_id_" + str(session['quiz_id']) + "/student_" + str(session['id'])
    path = os.path.join(parent_dir, directory)

    if os.path.isdir(path):
        return

    os.makedirs(path)
    for folder in folders:
        new_path = os.path.join(path, folder)
        os.mkdir(new_path)
