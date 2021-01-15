# Flask classes imported #
import os
from flask import (
    Flask, render_template, request, 
    flash, redirect, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


# App variable defined#


app = Flask(__name__)


# Config vars defined and added to Heroku#


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes")
def recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        flash("Thanks {}, for logging in!".format(request.form.get("email")))
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


# change to false before submitting #


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)
