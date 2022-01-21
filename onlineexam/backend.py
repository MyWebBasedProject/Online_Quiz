from onlineexam import mydb
# myCursor.execute(
#     "CREATE TABLE temp_report (report_id  int, message varchar(50) NOT NULL, screenshot blob) "
# )


class BackendOperations:
    def digital_to_binary(self, image_name):
        with open(image_name, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def insert_message(self, msg, image_name):
        cursor = mydb.connection.cursor()
        try:
            print("Record Insertertion Started")
            #picture = self.digital_to_binary(image_name)

            #cursor.execute('INSERT INTO temp_report(message, screenshot) VALUES (%s, %s)', (msg, image_name, ))
            # mydb.connection.commit()
            #print("Record Inserted")

        except Exception as error:
            print("The error occured  is {}".format(error))

        finally:
            cursor.close()
