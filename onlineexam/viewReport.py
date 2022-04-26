from onlineexam import mydb


def getViolationCount():
    cursor = mydb.connection.cursor()
    violations = []
    cursor.execute(
        'SELECT COUNT(message) FROM temp_report WHERE message="No Face Detected"')
    violations.append(cursor.fetchone())
    cursor.execute(
        'SELECT COUNT(message) FROM temp_report WHERE message="Multiple Faces Detected"')
    violations.append(cursor.fetchone())
    cursor.execute(
        'SELECT COUNT(message) FROM temp_report WHERE message="Wrong Person"')
    violations.append(cursor.fetchone())
    cursor.execute(
        'SELECT COUNT(message) FROM temp_report WHERE message="Looking Left"')
    violations.append(cursor.fetchone())
    cursor.execute(
        'SELECT COUNT(message) FROM temp_report WHERE message="Looking Right"')
    violations.append(cursor.fetchone())
    cursor.close()
    return violations


def getViolationAndImage(message):
    cursor = mydb.connection.cursor()
    if message == 'All':
        cursor.execute('SELECT * FROM temp_report where 1')
    elif message == 'Face Left Side':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Face Left Side" ')
    elif message == 'Face Right Side':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Face Right Side"')
    elif message == 'Looking Left':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Looking Left" ')
    elif message == 'Looking Right':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Looking Right" ')
    elif message == 'Multiple Person Detected':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Multiple Person Detected" ')
    elif message == 'No Face Detected':
        cursor.execute(
            'SELECT * FROM temp_report where message = "No Face Detected" ')
    elif message == 'Switched Application':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Switched Application" ')
    elif message == 'Mobile Detected':
        cursor.execute(
            'SELECT * FROM temp_report where message = "Mobile Detected" ')
    else:
        cursor.execute(
            'SELECT * FROM temp_report where message = "Wrong Person" ')
    violation = cursor.fetchall()
    cursor.close()
    return violation
