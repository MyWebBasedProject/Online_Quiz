import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL,MySQLdb
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import base64
import random
import string
from PIL import Image 
import io
import urllib.request
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'o9LBNl1iwuXs9oB4jnrSng'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'project'
mysql = MySQL(app)

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'onlinequizexamination@gmail.com'
app.config['MAIL_PASSWORD'] = 'April@1716'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

student = 'static/profilepics/student/'
app.config['student'] = student

teacher = 'static/profilepics/teacher/'
app.config['teacher'] = teacher

question_image = 'static/question_image/'
app.config['question_image'] = question_image

def remove(string):
    return string.replace(" ", "")

@app.route('/')
def home():
	return render_template('HomePage.html') 

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'category' in request.form:
		email = request.form['email']
		password = request.form['password']
		category = request.form['category']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM ' + category +' WHERE email = % s ', (email, ))
		account = cursor.fetchone()
		if account:
			cursor.execute('SELECT * FROM ' + category +' WHERE email = % s AND password = % s', (email, password, ))
			pwd = cursor.fetchone()
			if pwd:
				session['loggedin'] = True
				session['first_name'] = pwd['first_name']
				session['middle_name'] = pwd['middle_name']
				session['last_name'] = pwd['last_name']
				session['profile_pic'] = pwd['profile_pic']
				session['email'] = pwd['email']
				session['id'] = pwd['id']
				if category == 'student':
					return redirect(url_for("student"))
					
				else:
					return redirect(url_for("teacher"))
			else:
				msg = 'Invalid Credentials'
				return render_template('Homepage.html', msg=msg)
		else:
			msg = 'Register first!'
			return render_template('HomePage.html', msg = msg)

@app.route('/forgot')
def forgot():
	return render_template('forgot.html')

@app.route('/Register')
def register():
	return render_template('Register.html')

@app.route('/TeacherSignUp', methods =['GET', 'POST'])
def TeacherSignUp():
	msg= ''
	if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'middle_name' in request.form and 'dob' in request.form and 'age' in request.form and  'email' in request.form and 'password' in request.form and 'Confirm_password' in request.form and 'profile_pic' in request.files:	
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		middle_name = request.form['middle_name']
		dob = request.form['dob']
		age = request.form['age']
		email = request.form['email']
		password = request.form['password']
		c_password = request.form['Confirm_password']
		profile_pic =request.files['profile_pic']

		if not first_name or not last_name or not middle_name or not dob or not age or not email or not password or not c_password or not profile_pic:
			msg = 'Please fill out the form !'
			return render_template('TeacherSignUp.html', msg=msg)
		else:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM teacher WHERE email = % s ', (email, ))
			account = cursor.fetchone()
			if account:
				msg = 'Account already exists !'
				return render_template('TeacherSignUp.html', msg=msg)
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
				return render_template('TeacherSignUp.html', msg=msg)
			elif not password == c_password:
				msg = "Paswords doesn't match"
				return render_template('TeacherSignUp.html', msg=msg)
			else:
				name ='%s%s%s'%(first_name,middle_name,last_name)
				name = remove(name)
				filename = secure_filename(name)
				profile_pic.save(os.path.join(app.config['teacher'], filename))
				profile_pic = "http://127.0.0.1:5000/static/profilepics/teacher/%s"%(name)
				id=random.randint(0000,9999)
				cursor.execute('INSERT INTO teacher VALUES (%s, %s, % s, % s, % s, % s, % s, % s, % s)',
				(id, profile_pic, first_name, last_name, middle_name, dob, age, email, password, ))
				mysql.connection.commit()
				msg = '%s %s, you have successfully registered ! Your Id is %s'%(first_name,last_name,id)
				return render_template('HomePage.html', msg=msg)
	return render_template('TeacherSignUp.html', msg=msg)

@app.route('/StudentSignUp', methods =['GET', 'POST'])
def StudentSignUp():
	msg= ''
	if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'middle_name' in request.form and 'dob' in request.form and 'age' in request.form and  'email' in request.form and 'password' in request.form and 'Confirm_password' in request.form and 'branch' in request.form and 'semester' in request.form and 'profile_pic' in request.files:	
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		middle_name = request.form['middle_name']
		dob = request.form['dob']
		age = request.form['age']
		email = request.form['email']
		password = request.form['password']
		c_password = request.form['Confirm_password']
		branch = request.form['branch']
		semester = request.form['semester']
		profile_pic =request.files['profile_pic']

		if not first_name or not last_name or not middle_name or not dob or not age or not email or not password or not c_password or not branch or not semester or not profile_pic:
			msg = 'Please fill out the form !'
			return render_template('StudentSignUp.html', msg=msg)
		else:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM student WHERE email = % s ', (email, ))
			account = cursor.fetchone()
			if account:
				msg = 'Account already exists !'
				return render_template('StudentSignUp.html', msg=msg)
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
				return render_template('StudentSignUp.html', msg=msg)
			elif not password == c_password:
				msg = "Paswords doesn't match"
				return render_template('StudentSignUp.html', msg=msg)
			else:
				name = '%s%s%s'%(first_name, middle_name, last_name)
				name = remove(name)
				filename = secure_filename(name)
				profile_pic.save(os.path.join(app.config['student'], filename))
				profile_pic = "http://127.0.0.1:5000/static/profilepics/student/%s"%(name)
				id=random.randint(0000,9999)
				cursor.execute('INSERT INTO student VALUES (%s, %s, % s, % s, % s, % s, % s, % s, % s, %s, %s)',
				(id, profile_pic, first_name, last_name, middle_name, dob, age, email, password, branch, semester, ))
				mysql.connection.commit()
				msg = '%s %s, you have successfully registered ! Your Id is %s'%(first_name,last_name,id)
				return render_template('HomePage.html', msg=msg)
	return render_template('StudentSignUp.html', msg=msg)

@app.route('/student', methods=['GET', 'POST'])
def student():
	email = session['email']
	firstname = session['first_name']
	profilepic = session['profile_pic']
	msg = 'Welcome, %s'%(firstname)
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	return render_template('student.html', msg =msg, details = profilepic)

@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
	email = session['email']
	firstname = session['first_name']
	profilepic = session['profile_pic']
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	return render_template('teacher.html', details = profilepic)

@app.route('/Qcreate', methods=['GET', 'POST'])
def QCreate():
	teacher_id = session['id']
	code = ''.join(random.choices(string.ascii_uppercase + string.digits , k = 4))
	session['code']=code
	if request.method == "POST" and 'title' in request.form and 'branch' in request.form and 'sem' in request.form and 'subject' in request.form and 'password' in request.form and 'questions' in request.form and 'duration' in request.form and 'date' in request.form and 'start_time' in request.form:
		title = request.form['title']
		session['title'] = title
		branch = request.form['branch']
		session['branch'] = branch
		sem = request.form['sem']
		session['sem'] = sem
		subject = request.form['subject']
		session['subject'] = subject
		password = request.form['password']
		session['password'] = password
		questions = request.form['questions']
		session['questions'] = questions
		duration = request.form['duration']
		session['duration'] = duration
		date = request.form['date']
		session['date'] = date
		start_time = request.form['start_time']
		session['start_time'] = start_time
		if not title or not branch or not sem or not subject or not password or not questions or not duration or not date or not start_time:
			msg = "Please fill out the form"
			return render_template('QCreate.html',id=teacher_id, code=code, msg = msg)
		else:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute("CREATE TABLE IF NOT EXISTS "+ code +
			"""(question_code varchar(100) NOT NULL PRIMARY KEY, 
				question varchar(1000), 
				image varchar(1000), 
				option_1 varchar(1000), 
				option_2 varchar(1000), 
				option_3 varchar(1000), 
				option_4 varchar(1000), 
				answer varchar(1000)) 
				ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;""")
			mysql.connection.commit()
			cursor.execute('INSERT INTO quiz_details VALUES (%s, %s, % s, % s, % s, % s, % s, % s, % s, %s, %s)', 
			(code, teacher_id, title, branch, sem, subject, password, questions, duration, date, start_time, ))
			mysql.connection.commit()
			cursor.execute("SELECT id FROM student where branch = %s and semester = %s",(branch ,sem, ))
			row = cursor.fecthall()
			for id in row:
				student = id
				cursor.execute("ALTER TABLE %s ADD COLUMN %s varchar(1000)",(code, student, ))
			return redirect(url_for("Quiz"))
	return render_template('Qcreate.html', id=teacher_id, code=code)

@app.route('/Quiz', methods=['GET', 'POST'])
def Quiz():
	msg =" "
	code = session['code']
	no = session['questions']
	profile_pic = session['profile_pic']
	n = int(no)
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	if request.method == "POST" and 'qno' in request.form and 'question' in request.form and 'image' in request.files and 'option_1' in request.form and 'option_2' in request.form and 'option_3' in request.form and 'option_4' in request.form and 'answer' in request.form:
		qno = request.form['qno']
		question = request.form['question']
		image = request.files['image']
		option_1 = request.form['option_1']
		option_2 = request.form['option_2']
		option_3 = request.form['option_3']
		option_4 = request.form['option_4']
		answer = request.form['answer']
		name = "%s%s"%(code,qno)
		question_code = remove(name)
		if answer == "option_1":
			answer = option_1
		elif answer == "option_2":
			answer = option_2
		elif answer == "option_3":
			answer = option_3
		elif answer == "option_4":
			answer = option_4
		if image:
			filename = secure_filename(question_code)
			image.save(os.path.join(app.config['question_image'], filename))
			image = "http://127.0.0.1:5000/static/question_image/%s"%(question_code)
		else:
			image = "NULL"
		if not qno or not option_1 or not option_2 or not option_3 or not option_4 or not answer:
			msg = "Please fill out the form"
			return render_template('Quiz.html', msg=msg)
		else:
			cursor.execute('INSERT INTO quiz_exam VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
			(code, question_code, question, image, option_1, option_2, option_3, option_4, answer, ))
			mysql.connection.commit()
			rows = cursor.execute('select * from quiz_exam where code=%s',(code, ))
			if (rows >= n):
				msg = "Quiz for "+session['subject']+" has been Schedule on "+session['date']
				cursor.execute("SELECT email FROM student where branch = %s and semester = %s",(session['branch'] ,session['sem'], ))
				recipient = cursor.fetchall()
				quiz = Message(subject = msg,
								sender = "onlinequizexamination@gmail.com",
								recipients = [recipient])
				quiz.body = "This is to inform you that quiz has been created for "+session['subject']+" on "+session['date']+". Test details are as follows : \r\n Subject: "+session['subject']+"\r\n Title: "+session['title']+"\r\n Quiz Code: "+session['code']+"\r\n Password: "+session['password']+"\r\n Date :"+session['date']+"\r\n Duration :"+session['duration']+"\r\n Start Time: "+session['start_time'] 
				mail.send(quiz)
				return render_template('teacher.html', msg=msg, details= profile_pic)
	return render_template('Quiz.html', msg=msg, n=n)

@app.route('/StartQuiz', methods=['GET', 'POST'])
def StartQuiz():
	return render_template('StartQuiz.html')

@app.route('/logout') 
def logout():
	session.clear()
	return redirect(url_for("home"))

if __name__ == "__main__":
   app.run()