# to run locally: python -m flask --app .\main.py run

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello world from my lil Flask app"