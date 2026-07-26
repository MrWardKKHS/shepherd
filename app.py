from flask import Flask, render_template, abort, session, request, redirect, flash
from livereload import Server
import sqlite3
from pathlib import Path

#super cool functions to generate and check password password hashes
from werkzeug.security import generate_password_hash, check_password_hash

DB = 'db.db'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "MyReallySecretKey"
UPLOAD_FOLDER = Path("static/images/uploads")

def query_db(sql, args=(), one=False):
    """Connect to the db and run the provided query
    Returns a list of dicts, a single dict OR an error
    Will also execute INSERT, UPDATE and DELETE
    """
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    try:
        cursor.execute(sql, args)
        # Convert rows into dicts
        results = [dict(row) for row in cursor.fetchall()]
        db.commit()

        if not results:
            return None
        if one:
            return results[0]
        else:
            return results

    except Exception as e:
        print(e)
        return e

    finally:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["GET","POST"])
def login():
    """Route to handle logging in. 

    Redirects successful logins to the requested page
    or to the home page if no URL was provided
    """
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
            if check_password_hash(user['password'] ,password):
                #we are logged in successfully
                #Store the username in the session
                session['user'] = user
                flash("Logged in successfully")

                # Check for a requested return ULR in query params i.e. ?redirect=register-a-farm
                redirect_location = request.args.get('redirect')

                if redirect_location:
                    return redirect("/" + redirect_location)
                else:
                    # Send the user to home if no redirect param
                    return redirect('/')
            else:
                flash("Password incorrect", category="error")
        else:
            flash("Username does not exist", category='error')

    #render this template regardles of get/post
    return render_template('login.html')

@app.route('/signup', methods=["GET","POST"])
def signup():
    #if the user posts from the signup page
    if request.method == "POST":
        #add the new username and hashed password to the database
        username = request.form['username']
        password = request.form['password']
        #hash it with the cool secutiry function
        hashed_password = generate_password_hash(password)
        #write it as a new user to the database
        sql = "INSERT INTO user (username,password) VALUES (?,?)"
        res = query_db(sql,(username,hashed_password))
        if isinstance(res, Exception):
            if isinstance(res, sqlite3.IntegrityError):
                flash("Username already exists")
            else: 
                flash("An error has occured. Please try again")
        else: 
            #message flashes exist in the base.html template and give user feedback
            flash("Sign Up Successful")
            redirect('/')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    #just clear the username from the session and redirect back to the home page
    session['user'] = None
    return redirect('/')

@app.route("/register-a-farm")
def register_farm():
    if not session['user']:
        flash('Please log in to continue')
        return redirect('/login?redirect=register-a-farm')

    farm_types = query_db(
        """
        SELECT id, type
        FROM farmType
        ORDER BY type
        """
    )

    return render_template(
        "register-a-farm.html",
        farm_types=farm_types
    )


@app.post("/add_farm")
def add_farm():
    # User will always be logged in
    user_id = session['user']['uuid']

    # Following inputs are mandatory
    name = request.form["name"]
    address = request.form["address"]
    farm_type = request.form["type"]
    description = request.form["description"]
    website_url = request.form["website_url"]

    # unchecked checkboxes are not present in a form
    organic = request.form.get("organic", 0)

    filename = request.files["file"].filename
    file = request.files["file"]

    # Save the file to the uploads folder
    if file:
        file.save(UPLOAD_FOLDER / filename)

    sql = """
        INSERT INTO farms
        (user_id, name, address, image_src, description, farm_type, website_url, organic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    query_db(
        sql,
        (
            user_id, 
            name,
            address,
            filename,
            description,
            farm_type,
            website_url, 
            organic
        )
    )

    return redirect("/farms")

@app.route('/farms')
def farms():
    sql = """
        SELECT farms.*, farmType.type
        FROM farms
        JOIN farmType
            ON farms.farm_type = farmType.id
    """
    farms = query_db(sql)
    print(farms)
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
