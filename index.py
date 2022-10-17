from flask import Flask, render_template, url_for, redirect, session, request
import os
import mysql.connector as mysql
import hashlib

app = Flask(__name__)

app.secret_key = 'Jakkrit Onsomkrit'


#Connect MySQL Server
conn = mysql.connect(
    host = 'localhost', #IP Address
    user = 'root',
    passwd = '',
    port = 3306,
    database = 'test_abc'
)

template_folder = os.path.join(os.path.dirname(__file__), "templates/")
app.static_folder = 'static'
app.static_url_path = '/static'

@app.route('/', methods=["GET","POST"])
def index():
    session['user'] = ''
    session['audit'] = False
    return render_template("sign-in.html")

@app.route('/sign-up', methods=["GET","POST"])
def sign_up():
    return render_template("sign-up.html")

@app.route('/validate-sign-up', methods=["GET","POST"])
def validate_sign_up():
    name = request.form['fname']
    user = request.form['user']
    password = request.form['password']
    cfpassword = request.form['cfpassword']

    if name != "" and user != "" and password != "" and password == cfpassword:
        encypt_passwd = hashlib.md5(password.encode()).hexdigest()
        conn.reconnect()
        cur = conn.cursor() #Connected MySQL Server
        insert_sql = """
            INSERT INTO username(username,password,fullname,audit)
            VALUES(%s,%s,%s,%s)
        """
        val = (user,encypt_passwd,name,1)
        cur.execute(insert_sql,val)
        conn.commit()
        conn.close()
        return render_template('sign-up-success.html')
    else:
        return render_template('sign-up.html')

@app.route('/validate-sign-in', methods =["GET","POST"])
def validate_sign_in():
    user = request.form['user']
    passwd = request.form['password']
    if user != '' and passwd != '':
        sql = '''
            SELECT password FROM username 
            WHERE username=%s        
            '''
        val = (user,)

        conn.reconnect()
        cur = conn.cursor()
        cur.execute(sql,val)
        data = cur.fetchone()
        conn.close()

        encypt_passwd = hashlib.md5(passwd.encode()).hexdigest()
        if data[0] == encypt_passwd:
            session['user'] = user
            session['audit'] = True
            return render_template('sign-in-success.html')
        else:
            return render_template('sign-in.html')
    else:
        return render_template('sign-in.html')

@app.route('/main-program', methods =["GET","POST"])
def main_program():
    if session['audit'] == True:
        return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)