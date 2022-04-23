from onlineexam import mydb
from flask import session

def getViolationCount():
    cursor = mydb.connection.cursor()
    total_violation_seconds = 0
    table = session["report_code"] + "_report"
    student_id = session["report_student_id"]

    sql_query = f'SELECT violation_time FROM `{table}` WHERE student_roll_no = {student_id}'
    cursor.execute(sql_query)
    total_violation_seconds  = cursor.fetchall()

    cursor.close()
    return total_violation_seconds


def getViolationAndImage(message):
    cursor = mydb.connection.cursor()
    table = session["report_code"] + "_report"
    student_id = session["report_student_id"]

    if message == 'All':
        sql_query = f'SELECT * FROM `{table}` where `student_roll_no` = {student_id}'
        cursor.execute(sql_query)
    elif message == 'Face Left Side':
        sql_query = f'SELECT * FROM `{table}` where `student_roll_no` = {student_id} AND msg = "Face Left Side"'
        cursor.execute(sql_query)
    elif message == 'Face Right Side':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Face Right Side"'
        cursor.execute(sql_query)
    elif message == 'Looking Left':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Looking Left"'
        cursor.execute(sql_query)
    elif message == 'Looking Right':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Looking Right"'
        cursor.execute(sql_query)
    elif message == 'Multiple Person Detected':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Multiple Person Detected"'
        cursor.execute(sql_query)
    elif message == 'No Face Detected':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "No Face Detected"'
        cursor.execute(sql_query)
    elif message == 'Switched Application':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Switched Application"'
        cursor.execute(sql_query)
    elif message == 'Mobile Detected':
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Mobile Detected"'
        cursor.execute(sql_query)
    else:
        sql_query = f'SELECT * FROM `{table}` where student_roll_no = {student_id} AND msg = "Wrong Person"'
        cursor.execute(sql_query)
    violation = cursor.fetchall()
    cursor.close()
    return violation
