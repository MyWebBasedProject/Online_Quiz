from flask import render_template, request
from onlineexam import app, viewReport, mydb
import pyautogui
import time

@app.route("/take_screenShot", methods=['POST'])
def takeScreenShot():
    if request.method == "POST":
        count = request.form['count']
        time.sleep(0.15)
        img = pyautogui.screenshot()
        myCursor = mydb.connection.cursor()
        path = "static/temp_report/Switched_Application/" + str(count) + ".png"
        img.save('onlineexam/' + path)
        myCursor.execute(
            'INSERT INTO temp_report(message, screenshot) VALUES (%s, %s)', ('Switched_Application', path,))
        mydb.connection.commit()
        myCursor.close()
        return "1"


@app.route("/show_records_and_images", methods=['POST'])
def printReport():
    if request.method == "POST":
        print("print Report")
        records_images_tuple = viewReport.getVioaltionAndImage()
        record_images = {}
        for i in records_images_tuple:
            record_images[i[0]] = {
                "message": i[1],
                "image": str(i[2]),
                "time": str(i[3])
            }

        return record_images


@app.route("/")
def home():
    print("redirected")
    return render_template("index.html")


@app.route("/face_detect", methods=["POST"])
def faceDetect():
    if request.method == "POST":
        return render_template("face_detect.html")


@app.route("/view_report", methods=["POST"])
def view_report_template():
    if request.method == "POST":
        return render_template("view_report.html")
