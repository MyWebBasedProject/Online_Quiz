from onlineexam import mydb
from flask import session


def getViolationCount():
    cursor = mydb.connection.cursor()
    total_violation_seconds = 0
    table = session["class_id"] + "_" + session['quiz_id'] + "_report"
    student_id = session["student_exam_id"]
    print(student_id)

    sql_query = f'SELECT violation_time FROM `{table}` WHERE student_id = {student_id}'
    cursor.execute(sql_query)
    total_violation_seconds = cursor.fetchall()
    cursor.close()
    return total_violation_seconds


def getViolationAndImage(message):
    cursor = mydb.connection.cursor()
    table = session["class_id"] + "_" + session["quiz_id"] + "_report"
    student_id = session["student_exam_id"]
    print(student_id)
    if message == 'All':
        sql_query = f'SELECT * FROM `{table}` where `student_id` = {student_id}'
        cursor.execute(sql_query)
    elif message == 'Face Left Side':
        sql_query = f'SELECT * FROM `{table}` where `student_id` = {student_id} AND `error_msg` = "Face Left Side"'
        cursor.execute(sql_query)
    elif message == 'Face Right Side':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Face Right Side"'
        cursor.execute(sql_query)
    elif message == 'Looking Left':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Looking Left"'
        cursor.execute(sql_query)
    elif message == 'Looking Right':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Looking Right"'
        cursor.execute(sql_query)
    elif message == 'Multiple Person Detected':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Multiple Person Detected"'
        cursor.execute(sql_query)
    elif message == 'No Face Detected':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "No Face Detected"'
        cursor.execute(sql_query)
    elif message == 'Switched Application':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Switched_Application"'
        cursor.execute(sql_query)
    elif message == 'Mobile Detected':
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Mobile Detected"'
        cursor.execute(sql_query)
    else:
        sql_query = f'SELECT * FROM `{table}` where student_id = {student_id} AND `error_msg` = "Wrong Person"'
        cursor.execute(sql_query)
    violation = cursor.fetchall()
    cursor.close()
    return violation
