# FLASK CLASSES IMPORTED #
import os
from flask import (
    Flask, render_template, request,
    flash, redirect, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


# APP VAR DEFINED #


app = Flask(__name__)


# CONFIG VARS #


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# APP OPENS ON INDEX PAGE #


@app.route("/")
# When app is started, the homepage is rendered#
def index():
    return render_template("index.html")


# RECIPES  #


@app.route("/recipes")
# Returns recipes as list from DB#
def recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/search", methods=["GET", "POST"])
# Allows user to text search, which return matching queries
# from recipe name, category & ingredients as defined in DB index #
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


# USER CAN REGISTER #


@app.route("/register", methods=["GET", "POST"])
# A user can register for a new account, if the user is already
# registered they will be redirected to register page, otherwise
# they are taken to their profile page#
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists - Please log in")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registeration complete!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# EXISTING USERS LOGIN #


@app.route("/login", methods=["GET", "POST"])
# Allows users with registered accounts to log in #
def login():
    if request.method == "POST":
        # Checks if a username already exists in db #
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Checks that hashed password matches user input #
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back {}!".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Password doesn't match, redirects to login page#
                flash("Password incorrect, please try again")
                return redirect(url_for("login"))

        else:
            # User doesn't exist, redirects to login page #
            flash("Incorrect username and/or password")
            return redirect(url_for("login"))

    return render_template("login.html")


# USER CAN VIEW OWN RECIPES ON PROFILE #


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # User's username and own recipes are taken from DB and display on page#
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    recipes = list(mongo.db.recipes.find())

    if session["user"]:
        return render_template(
            "profile.html", username=username, recipes=recipes)

    return redirect(url_for("login"))


# LOG OUT #


@app.route("/logout")
def logout():
    # Removes user from session cookies and logs the user out #
    # and redirects to login page#
    flash("You've been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# ADD RECIPE #


@app.route("/add_recipe", methods=["GET", "POST"])
# User can add a recipe by filling in the fields, these correlate
# with fields in the DB - user receives feedback when
# a recipe has been added successfully
def add_recipe():
    if request.method == "POST":
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"],
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe added successfully!")
        return redirect(url_for("recipes"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


# VIEW RECIPE #


@app.route("/view_recipe/<recipe_id>", methods=["GET"])
# User can view each recipe individually, recipe creator
# can also edit/delete from this page #
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("view_recipe.html", recipe=recipe)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
# Allows a user to edit or delete a recipe added by themselves,
# they are only able to view recipes added by other users#
def edit_recipe(recipe_id):
    if request.method == "POST":
        recipe_submit = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"],
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, recipe_submit)
        flash("Recipe has been updated!")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/delete_recipe/<recipe_id>")
# User can delete their own recipes, this is removed from the DB#
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe deleted")
    return redirect(url_for("recipes"))


@app.route("/delete_profile/<username>")
# User can delete their own profile, user's recipes are kept #
def delete_profile(username):
    mongo.db.users.remove({"username": username.lower()})
    session.pop("user")
    flash("Your profile has been deleted")
    return redirect(url_for("register"))


# ADMIN ONLY FUNCTIONS #


@app.route("/view_users")
# Returns user list, admin is not counted#
# as part of this and 'popped' from list #
# If user is not 'admin' they will be redirected back to index #
def view_users():
    users = list(
        mongo.db.users.find())
    for i, user in enumerate(users):
        if user["username"] == "admin":
            users.pop(i)
            break

    if session["user"] == "admin":
        return render_template("view_users.html", users=users)

    else:
        return redirect(url_for("index"))


@app.route("/admin_delete_recipe/<recipe_id>")
# Admin can delete any user's recipe, this is removed from the DB#
def admin_delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe deleted")
    return redirect(url_for("recipes"))


@app.route("/delete_user/<user_id>")
# Admin can delete users from the database and is returned to view users page#
def delete_user(user_id):
    mongo.db.users.remove({"_id": ObjectId(user_id)})
    flash("User deleted")
    return redirect(url_for("view_users"))


# DEBUG #


if __name__ == "__main__":
    # Changed to false before submitting #
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=False)
