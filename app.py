from flask import Flask, render_template, abort
from livereload import Server
import sqlite3

DB = 'db.db'

app = Flask(__name__)
app.debug = True

def query_db(sql, one=False):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute(sql)
    if one: 
        return cursor.fetchone()
    else:
        return cursor.fetchall()

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