import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL,MySQLdb
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import base64
import random
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
app.config['MAIL_USERNAME'] = 'yourId@gmail.com'
app.config['MAIL_PASSWORD'] = '*****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

student = 'static/profilepics/student/'
app.config['student'] = student

teacher = 'static/profilepics/teacher/'
app.config['teacher'] = teacher

def remove(string):
    return string.replace(" ", "")

@app.route('/')
def home():
	return render_template('HomePage.html') 

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
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
	
	msg = Message(
                'Hello',
                sender ='yourId@gmail.com',
                recipients = ['receiver’sid@gmail.com']
               )
	msg.body = 'Hello Flask message sent from Flask-Mail'
	mail.send(msg)
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
				cursor.execute('INSERT INTO teacher VALUES (%s, %s, % s, % s, % s, % s, % s, % s, % s)', (id, profile_pic, first_name, last_name, middle_name, dob, age, email, password, ))
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
				cursor.execute('INSERT INTO student VALUES (%s, %s, % s, % s, % s, % s, % s, % s, % s, %s, %s)', (id, profile_pic, first_name, last_name, middle_name, dob, age, email, password, branch, semester ))
				mysql.connection.commit()
				msg = '%s %s, you have successfully registered ! Your Id is %s'%(first_name,last_name,id)
				return render_template('HomePage.html', msg=msg)
	return render_template('StudentSignUp.html', msg=msg)

@app.route('/student')
def student():
	email = session['email']
	firstname = session['first_name']
	profilepic = session['profile_pic']
	msg = 'Welcome, %s'%(firstname)
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	return render_template('student.html', msg =msg, details = profilepic)

@app.route('/teacher')
def teacher():
	email = session['email']
	firstname = session['first_name']
	profilepic = session['profile_pic']
	msg = 'Welcome, %s'%(firstname)
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	return render_template('teacher.html', msg =msg, details = profilepic)

@app.route('/logout') 
def logout():
	session.pop('loggedin', None) 
	session.pop('categories', None) 
	session.pop('email', None)
	session.pop('first_name', None)
	session.pop('last_name', None)
	session.pop('profile_pic', None)
	return redirect(url_for("home"))


if __name__ == "__main__":
   app.run()