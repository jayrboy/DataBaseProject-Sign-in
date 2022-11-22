from flask import Flask, render_template, url_for, redirect, request, session
import mysql.connector as mysql
import sqlite3 as sql
import hashlib
import os
import random
import datetime

from numpy import full, record

app = Flask(__name__)
template_folder = os.path.join(os.path.dirname(__file__), "templates/")
app.static_folder = 'static'
app.static_url_path = '/static'

#size not over 4MB
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000 

app.secret_key = 'I-BIT Web Application'

#database 
database = os.path.join(os.path.dirname(__file__), "database/abc_company.db")

#upload folder
UPLOAD_IMG_FOLDER = os.path.join(os.path.dirname(__file__), "static/images")
UPLOAD_DOC_FOLDER = os.path.join(os.path.dirname(__file__), "static/document")

db = mysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        passwd = '12345678',
        database = 'test_db2'
    )

@app.route('/', methods=["GET"])
def index():
    return render_template("sign-in.html")

@app.route('/sign-in', methods=["GET"])
def sing_in():
    return render_template("sign-in.html")

@app.route('/sign-up', methods=["GET"])
def sign_up():
    return render_template("sign-up.html")

@app.route('/sign-out', methods=["GET"])
def sign_out():
    session.pop('username', None)
    session.pop('authorize', None)
    return redirect("/")

@app.route('/validate-sign-in', methods=["POST"])
def validate_sign_in():
    user = request.form.get('user')
    password = request.form.get('password')
    encypt_pass = hashlib.md5(password.encode()).hexdigest()

    if user !="" and password !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_query = """
        SELECT username,password FROM username WHERE username=? 
        """
        val = (user,)
        cur.execute(sql_query, val)
        record = cur.fetchone()
        conn.close()

        if record[1] == encypt_pass:
            session['username'] = user
            session['authorize'] = True
            return redirect("/main-program")
        else:
            return redirect("/error-sign-in")
    else:
        return redirect("/error-sign-in")

@app.route('/validate-sign-up', methods=["POST"])
def validate_sign_up():
    fullname = request.form.get('fname')
    user = request.form.get('user')
    password = request.form.get('password')
    cfpassword = request.form.get('cfpassword')
    encypt_pass = hashlib.md5(password.encode()).hexdigest()

    if fullname !="" and user !="" and password !="" and password == cfpassword:
        # conn = sql.connect(database)
        # cur = conn.cursor()
        cur = db.cursor()

        sql_insert = """
        INSERT INTO username(username,fullname,password,authorize)          
        VALUES (%s,%s,%s,%s) 
        """
        val = (user,fullname,encypt_pass,1)

        cur.execute(sql_insert, val)
        db.commit()
        db.close()
        # return redirect("/success-sign-up")
        return "test"
    else:
        return redirect("/error-sign-up")

@app.route('/error-sign-in', methods=["GET"])
def error_sign_in():
    return render_template("error-sign-in.html")

@app.route('/error-sign-up', methods=["GET"])
def error_sign_up():
    return render_template("error-sign-up.html")

@app.route('/success-sign-in', methods=["GET"])
def success_sign_in():
    return render_template("sign-in-success.html")

@app.route('/success-sign-up', methods=["GET"])
def success_sign_up():
    return render_template("sign-up-success.html")

#main program
@app.route('/main-program', methods=["GET"])
def main_program():
    if 'authorize' in session:
        return render_template("main.html")
    else:
        return render_template("sign-in.html")

#users
@app.route('/user', methods=["GET"])
def main_user():
    if 'authorize' in session:
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_query = """
        SELECT username,fullname,authorize FROM username order by fullname 
        """
        cur.execute(sql_query)
        users = cur.fetchall()
        conn.close()
        return render_template("user.html", users=users)
    else:
        return render_template("sign-in.html")

@app.route('/user-add', methods=["GET"])
def main_user_add():
    if 'authorize' in session:
        return render_template('user-add.html')
    else:
        return render_template("sign-in.html")

@app.route('/user-add-post', methods=["POST"])
def main_user_add_post():
    if 'authorize' in session:
        fullname = request.form.get('fname')
        user = request.form.get('user')
        password = request.form.get('password')
        cfpassword = request.form.get('cfpassword')
        encypt_pass = hashlib.md5(password.encode()).hexdigest()

        if fullname !="" and user !="" and password !="" and password == cfpassword:
            conn = sql.connect(database)
            cur = conn.cursor()
            sql_insert = """
            INSERT INTO username(username,fullname,password,authorize)          
            VALUES (?,?,?,?) 
            """
            val = (user,fullname,encypt_pass,1)
            cur.execute(sql_insert, val)
            conn.commit()
            conn.close()
            return redirect("/user")
        else:
            return redirect("/user-add")
    else:
        return render_template("sign-in.html")

@app.route('/user-edit/<user>', methods=["GET"])
def main_user_edit(user):
    if 'authorize' in session:
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_query = """
        SELECT username,fullname,authorize FROM username WHERE username = ? 
        """
        val = (user,)
        cur.execute(sql_query, val)
        users = cur.fetchone()
        conn.close()
        return render_template("user-edit.html", users=users)
    else:
        return render_template("sign-in.html")

@app.route('/user-edit-post', methods=["POST"])
def main_user_edit_post():
    if 'authorize' in session:
        fullname = request.form.get('fname')
        user = request.form.get('user')
        password = request.form.get('password')
        cfpassword = request.form.get('cfpassword')
        encypt_pass = hashlib.md5(password.encode()).hexdigest()

        if fullname !="" and user !="" and password !="" and password == cfpassword:
            conn = sql.connect(database)
            cur = conn.cursor()
            sql_update = """
            UPDATE username SET fullname=?,password=?,authorize=?          
            WHERE username=?
            """
            val = (fullname,encypt_pass,1,user)
            cur.execute(sql_update, val)
            conn.commit()
            conn.close()
            return redirect("/user")
        else:
            return redirect("/user")
    else:
        return render_template("sign-in.html")

@app.route('/user-delete/<user>', methods=["GET"])
def main_user_delete(user):
    if 'authorize' in session:
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_del = """
        DELETE FROM username WHERE username=?          
        """
        val = (user,)
        cur.execute(sql_del, val)
        conn.commit()
        conn.close()
        return redirect('/user')
    else:
        return render_template("sign-in.html")

@app.route("/upload", methods=["GET"])
def upload():
    return render_template('upload.html')

@app.route("/upload-file", methods=["POST"])
def upload_file():
    x = datetime.datetime.now()
    f = request.files['file']
    f2 = request.files['file2']
    
    nfile1 = f.filename.split(".")

    nfile1 = str(x.year) + str(x.month) + str(x.day) + "_" + str(random.randint(000000,999999)) + "." + nfile1[1]
    nfile2 = f2.filename.split(".")
    nfile2 = str(x.year) + str(x.month) + str(x.day) + "_" + str(random.randint(000000,999999)) + "." + nfile2[1]
    f.save(os.path.join(UPLOAD_IMG_FOLDER, nfile1))
    f2.save(os.path.join(UPLOAD_DOC_FOLDER, nfile2))
    return "File uploaded successfully!" 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) #127.0.0.1
