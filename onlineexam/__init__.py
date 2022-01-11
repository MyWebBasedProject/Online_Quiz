from flask import Flask
from flask_socketio import SocketIO
from flask_mysqldb import MySQL


app= Flask(__name__)
app.config['SECRET_KEY']='secret!'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'exam'

socketio = SocketIO(app)
mydb = MySQL(app)

from onlineexam import webapp, testing