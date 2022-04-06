from onlineexam import quiz
class BackendOperations:

    def insert_message(self, msg, image_path, mydb, violationTime):

        cursor = mydb.cursor()


        try:
            if quiz.student_id:
                table = str(quiz.quiz_code)+"_report"
                sql_query = f"INSERT INTO `{table}` (msg,student_roll_no, image_path, violation_time) VALUES (%s, %s, %s, %s)"
                data = [msg, quiz.student_id, image_path, violationTime]
                cursor.execute(sql_query, data)
                mydb.commit()

        except Exception as error:
            print("The error occured  is {}".format(error))
        finally:
            cursor.close()

