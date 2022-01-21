from flask import render_template
from onlineexam import app


@app.route("/")
def home():
    print("redirected")
    return render_template("index.html")
