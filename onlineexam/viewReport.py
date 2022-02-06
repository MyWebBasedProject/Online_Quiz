from onlineexam import mydb

def getViolationCount():
    cursor = mydb.connection.cursor()
    violations = []
    cursor.execute('SELECT COUNT(message) FROM temp_report WHERE message="No Face Detected"')
    violations.append(cursor.fetchone())
    cursor.execute('SELECT COUNT(message) FROM temp_report WHERE message="Multiple Faces Detected"')
    violations.append(cursor.fetchone())
    cursor.execute('SELECT COUNT(message) FROM temp_report WHERE message="Wrong Person"')
    violations.append(cursor.fetchone())
    cursor.execute('SELECT COUNT(message) FROM temp_report WHERE message="Looking Left"')
    violations.append(cursor.fetchone())
    cursor.execute('SELECT COUNT(message) FROM temp_report WHERE message="Looking Right"')
    violations.append(cursor.fetchone())
    cursor.close()
    return violations