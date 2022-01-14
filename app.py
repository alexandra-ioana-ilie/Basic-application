from flask import Flask, render_template, request, redirect, url_for, session
import re
import mysql.connector
from datetime import datetime

mydb= mysql.connector.connect(
     host= "localhost",
     user="root",
     password="root",
database="app"
)
 
app = Flask(__name__)
  
  
app.secret_key = '1234'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'app'
  
mycursor=mydb.cursor()

  
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        mycursor.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (username, password))
        account = mycursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'

            dateLogin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mycursor.execute("UPDATE accounts SET lastVisit = %s WHERE username = %s", (dateLogin, username))
            mydb.commit()

            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
  
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'city' in request.form and 'country' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        city = request.form['city']
        country = request.form['country']    
        
        mycursor.execute('SELECT * FROM accounts WHERE username = %s', (username, ))
        account = mycursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            dateREgistered = datetime.now().strftime('%Y-%m-%d')
            mycursor.execute("INSERT INTO accounts (username, password, email, city, country, joined) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, email, city, country, dateJoined))
            mydb.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
  
  
@app.route("/index")
def index():
    if 'loggedin' in session: 
        return render_template("index.html")
    return redirect(url_for('login'))
  
  
@app.route("/display")
def display():
    if 'loggedin' in session:
        # mycursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'], ))
        mycursor.execute('SELECT * FROM accounts WHERE username = %s', ('rzvcs', ))
        account =mycursor.fetchone()    
        return render_template("display.html", account = account)
    return redirect(url_for('login'))
  
@app.route("/update", methods =['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'city' in request.form and 'country' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            city = request.form['city']
            country = request.form['country']
            mycursor.execute('SELECT * FROM accounts WHERE username = %s', (username, ))
            account = mycursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'name must contain only characters and numbers !'
            else:
                mycursor.execute('UPDATE accounts SET username = %s, password = %s, email = %s, city = %s, country = %s WHERE id = %s', (username, password, email, city, country, session['id']))
                mydb.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg = msg)
    return redirect(url_for('login'))

@app.route("/statistics")
def statistics():
    if 'loggedin' in session:
        statistics = {
                'countAccounts':0, 
                'joinedToday': 0, 
                'latestVisit': 0 
            }
        
        dateToday = datetime.today().strftime('%Y-%m-%d')

        mycursor.execute('SELECT COUNT(username) from ACCOUNTS')
        statistics['countAccounts'] = mycursor.fetchone()[0]
        
        mycursor.execute('SELECT COUNT(username) from ACCOUNTS WHERE joined = %s', (dateToday,))
        statistics['joinedToday'] = mycursor.fetchone()[0]
        
        mycursor.execute('SELECT @lastVisit:=MIN(lastVisit) FROM accounts')
        mycursor.fetchone()
        mycursor.execute('SELECT username from ACCOUNTS WHERE lastVisit = @lastVisit')
        statistics['latestVisit'] = mycursor.fetchone()[0]
        
        return render_template("statistics.html", statistics = statistics)
    return redirect(url_for('login'))
  
if __name__ == "__main__":
    app.run(host ="localhost", port = int("8080"))
