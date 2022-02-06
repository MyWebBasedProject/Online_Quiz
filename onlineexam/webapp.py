from flask import render_template, request
from onlineexam import app, viewReport


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
        view_report = viewReport.getViolationCount()
        print(view_report)
        return render_template("view_report.html")