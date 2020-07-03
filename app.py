
from flask import Flask
from election_functions import init


app = Flask(__name__)
init()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/election/<year>")
def load_election_page(year):
    # Get data from respective JSON file and load HTML page using JSON to fill in template
    return "<p>wh0?</p>"