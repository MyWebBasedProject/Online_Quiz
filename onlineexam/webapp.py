from flask import render_template, request
from onlineexam import app, viewReport

@app.route("/show_records_and_images", methods=['POST'])
def printReport():
    if request.method == "POST":
        records_images_tuple = viewReport.getVioaltionAndImage()
        record_images = {}
        for i in records_images_tuple:
            record_images[i[0]] = {
                "message" : i[1],
                "image" : str(i[2]),
                "time" : str(i[3])
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