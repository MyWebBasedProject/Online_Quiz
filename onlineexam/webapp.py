from flask import render_template, request
from onlineexam import app


@app.route("/")
def home():
    print("redirected")
    return render_template("index.html")


@app.route("/face_detect", methods=["POST"])
def faceDetect():
    if request.method == "POST":
        return render_template("face_detect.html")
