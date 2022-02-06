
class BackendOperations:

    def digital_to_binary(self, image_name):
        with open(image_name, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def print_connection(self):
        print("connection")

    def insert_message(self, msg, image_name, mydb):

        #cursor = MySQLdb.connect()

        cursor = mydb.cursor()
        print("insert_meassage: cursor")
        print(cursor)
        try:

            # print("Record Insertertion Started")
            # picture = self.digital_to_binary(image_name)

            cursor.execute(
                'INSERT INTO temp_report(message, screenshot) VALUES (%s, %s)', (msg, image_name, ))
            mydb.commit()
            print("Record Inserted")

        except Exception as error:
            print("The error occured  is {}".format(error))
        finally:
            cursor.close()

