from flask import render_template, request, session
from onlineexam import app, viewReport, mydb, quiz
import pyautogui
import time


@app.route("/take_screenShot", methods=['POST'])
def takeScreenShot():
    if request.method == "POST":
        count = request.form['count']
        time.sleep(0.15)
        img = pyautogui.screenshot()
        myCursor = mydb.connection.cursor()
        img_name = str(count) + ".png"

        path = "static/" + session['code'] + "/"+ session['email'] +  "/Switched_Application/"
        img.save('onlineexam/' + path + img_name)
        violationTime = 1
        sql_query = 'INSERT INTO ' + session['code'] +  '_report (message, screenshot, violationTime) VALUES (Switched_Application,' + path +', ' + str(violationTime) +')'
        #print(sql_query)
        #myCursor.execute(sql_query)
        #mydb.connection.commit()
        myCursor.close()
        return "1"


@app.route("/show_records_and_images", methods=['POST'])
def printAllRecords():
    if request.method == "POST":
        message = request.form['option']
        #print(message)
        records_images_tuple = viewReport.getViolationAndImage(message)
        record_images = {}
        for i in records_images_tuple:
            record_images[i[0]] = {
                "message": i[1],
                "image": str(i[2]),
                "time": str(i[3]),
                "duration": str(i[4])
            }

        return record_images


@app.route('/')
def home():
    return render_template('HomePage.html')


@app.route("/face_detect", methods=["POST"])
def faceDetect():
    if request.method == "POST":
        return render_template("face_detect.html")


@app.route("/view_report", methods=["POST"])
def view_report_template():
    if request.method == "POST":
        return render_template("view_report.html")
