# Flask class imported #
import os
from flask import Flask, render_template, request, flash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")


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
