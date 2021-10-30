from flask import Flask, render_template, url_for, request, make_response
from werkzeug.utils import redirect
from pymongo import MongoClient

client = MongoClient()
db = client["flask-crud"]

app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/list", methods=["GET"])
def get_list():
	username = request.cookies.get("username")
	# if not username:
	# 	return redirect("/signup")

	friend_list = db.friend_list
	friends_number = friend_list.count()
	
	if friends_number > 0:
		friends = list(friend_list.find({"username": username}))
		return render_template(
			"list.html", friends=friends, username=username
			)
	return render_template("list.html", username=username)


@app.route("/list", methods=["POST"])
def create_friend():
	if request.method == "POST":
		username = request.cookies.get("username")
		friend_name = request.form["friendName"]
		social_link = request.form["socialLink"]
		# Create a new friend
		if not friend_name == '' and not social_link == '':
			friend_list = db.friend_list
			data = {
				"friend_name": friend_name,
				"social_link": social_link,
				"username": username
			}
			friend_list.insert_one(data)
		return redirect("/list")


@app.route("/signup", methods=["GET"])
def get_signup():
	return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def create_user():
	errors = []
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		password2 = request.form["password2"]
		
		# Validate if username is valid
		if not username:
			errors.append({
				"error": "user or password invalid",
				"data": {
					"username": username,
					"password": password
				}
			})
			return render_template("signup.html", errors=errors)
		
		# Check if the user is not duplicate
		user_exist = bool(db.users.find_one({"username": username}))
		if user_exist:
			errors.append({
				"error": "user already exist",
				"data": {
					"username": username,
					"password": password
				}
			})
			return render_template("signup.html", errors=errors)
		
		# Match passwords
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
		
		# cookie
		resp = make_response(render_template("index.html"))
		resp.set_cookie("username", username)
		return resp


@app.route("/signin", methods=["GET"])
def signin_user():
	return render_template("signin.html")