from flask import Flask
from flask_socketio import SocketIO
from flask_mysqldb import MySQL
from flask_mail import Mail

app = Flask(__name__)

app.secret_key = 'o9LBNl1iwuXs9oB4jnrSng'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'project'

mydb = MySQL(app)

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'onlinequizexamination@gmail.com'
app.config['MAIL_PASSWORD'] = 'April@1716'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

student = 'onlineexam/static/profilepics/student/'
app.config['student'] = student

teacher = 'onlineexam/static/profilepics/teacher/'
app.config['teacher'] = teacher

question_image = 'onlineexam/static/question_image/'
app.config['question_image'] = question_image


socketio = SocketIO(app)
