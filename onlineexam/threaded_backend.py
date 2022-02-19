
class BackendOperations:
    def insert_message(self, msg, image_path, mydb, violationTime):

        cursor = mydb.cursor()
        try:
            cursor.execute(
                'INSERT INTO temp_report(message, screenshot, violationTime) VALUES (%s, %s, %s)', (msg, image_path, violationTime, ))
            mydb.commit()

        except Exception as error:
            print("The error occured  is {}".format(error))
        finally:
            cursor.close()

