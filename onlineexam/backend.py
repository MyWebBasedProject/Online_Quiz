class BackendOperations:

    def insert_message(self, msg, image_path, mydb):

        cursor = mydb.cursor()
        print("insert_meassage: cursor")
        print(cursor)
        try:

            cursor.execute(
                'INSERT INTO temp_report(message, screenshot) VALUES (%s, %s)', (msg, image_path, ))
            mydb.commit()
            print("Record Inserted")

        except Exception as error:
            print("The error occured  is {}".format(error))
        finally:
            cursor.close()

