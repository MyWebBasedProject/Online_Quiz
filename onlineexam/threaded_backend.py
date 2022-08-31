from onlineexam import quiz


class BackendOperations:

    def insert_message(self, msg, image_path, mydb, violationTime):

        cursor = mydb.cursor()
        print(quiz.student_id)
        try:
            if quiz.student_id:
                table = str(quiz.class_id) + "_" + str(quiz.quiz_id)+"_report"
                sql_query = f"INSERT INTO `{table}` (error_msg,student_id, image_path, violation_time) VALUES (%s, %s, %s, %s)"
                print(image_path)
                data = [msg, quiz.student_id, image_path, violationTime]
                cursor.execute(sql_query, data)
                mydb.commit()

        except Exception as error:
            print("The error occured  is {}".format(error))
        finally:
            cursor.close()
