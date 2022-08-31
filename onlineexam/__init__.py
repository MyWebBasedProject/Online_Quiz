from flask import Flask
from flask_socketio import SocketIO
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'o9LBNl1iwuXs9oB4jnrSng'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'project'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mydb = MySQL(app)

student = 'onlineexam/static/profilepics/student/'
app.config['student'] = student

teacher = 'onlineexam/static/profilepics/teacher/'
app.config['teacher'] = teacher

question_image = 'onlineexam/static/Question Images/'
app.config['question_image'] = question_image

socketio = SocketIO(app)
