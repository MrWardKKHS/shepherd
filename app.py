from flask import Flask, render_template, abort, session, request, redirect, flash
from livereload import Server
import sqlite3

DB = 'db.db'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "MyReallySecretKey"

def query_db(sql, args=(), one=False):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute(sql, args)
    if one: 
        return cursor.fetchone()
    else:
        return cursor.fetchall()


@app.route('/login', methods=["GET","POST"])
def login():
    #if the user posts a username and password
    if request.method == "POST":
        #get the username and password
        username = request.form['username']
        password = request.form['password']
        #try to find this user in the database- note- just keepin' it simple so usernames must be unique
        sql = "SELECT * FROM user WHERE username = ?"
        user = query_db(sql=sql,args=(username,),one=True)
        if user:
            #we got a user!!
            #check password matches-
            if check_password_hash(user[2],password):
                #we are logged in successfully
                #Store the username in the session
                session['user'] = user
                flash("Logged in successfully")
            else:
                flash("Password incorrect")
        else:
            flash("Username does not exist")
    #render this template regardles of get/post
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/farms')
def farms():
    farms = query_db("SELECT * FROM farms")
    return render_template('farms.html', farms=farms)

@app.route('/apprentices')
def apprentices():
    return render_template('apprentices.html')

@app.route('/farms/<int:id>')
def single_farmer(id):
    sql = f"SELECT * FROM farms WHERE id={id}"
    farm = query_db(sql, one=True)
    if farm == None:
        abort(404)
    return render_template('farm-profile.html', farm=farm)

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

@app.errorhandler(404)
def page_not_found(error):
    # Pass the 404 status code as the second return value
    return render_template('404.html'), 404

if __name__ == "__main__":
    # Hot reload using live server
    server = Server(app.wsgi_app)
    server.watch("templates/")
    server.watch("static/")
    server.watch("static/")
    server.serve(
        port=5000,
        liveport=35729,
        debug=True
    )
