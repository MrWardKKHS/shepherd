from flask import Flask, render_template
from livereload import Server

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    # Hot reload using live server
    server = Server(app.wsgi_app)
    server.watch("templates/")
    server.watch("static/")
    server.watch("static/")
    server.serve(
        host="0.0.0.0",
        port=5000,
        liveport=35729,
        debug=True
    )