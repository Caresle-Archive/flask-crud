from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect
from pymongo import MongoClient

client = MongoClient()
db = client["flask-crud"]

app = Flask(__name__)


@app.route("/")
def index():
	url_for("static", filename="style.css")
	return render_template("index.html")


@app.route("/list", methods=["GET"])
def get_list():
	url_for("static", filename="style.css")
	friend_list = db.friend_list
	friends_number = friend_list.count()
	if friends_number > 0:
		friends = list(friend_list.find({}))
		print(friends)
		return render_template("list.html", friends=friends)
	return render_template("list.html")


@app.route("/list", methods=["POST"])
def create_friend():
	if request.method == "POST":
		friend_name = request.form["friendName"]
		social_link = request.form["socialLink"]
		if not friend_name == '' and not social_link == '':
			friend_list = db.friend_list
			data = {
				"friend_name": friend_name,
				"social_link": social_link
			}
			friend_list.insert_one(data)
		return redirect("/")


@app.route("/signup", methods=["GET"])
def get_signup():
	url_for("static", filename="style.css")
	return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def create_user():
	errors = []
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		password2 = request.form["password2"]
		
		if not username:
			errors.append({
				"error": "user or password invalid",
				"data": {
					"username": username,
					"password": password
				}
			})
			return render_template("signup.html", errors=errors)

		if not password == password2:
			errors.append({
				"error": "password doesn't match",
				"data": {
					"username": username,
					"password": password
				}
			})
			return render_template("signup.html", errors=errors)

		user_collection = db.users

		user = {
			"username": username,
			"password": password
		}

		user_collection.insert_one(user)
		return redirect("/")