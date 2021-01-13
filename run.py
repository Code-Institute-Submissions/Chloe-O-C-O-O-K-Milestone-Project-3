# Flask class imported #
import os
from flask import Flask, render_template

# 2 spaces between functions for PEP8 compliance #

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/index_copy.html")
def index_test():
    return render_template("index_copy.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)


# change to false before submitting #