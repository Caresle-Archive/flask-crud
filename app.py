from flask import Flask, render_template, request, make_response
from werkzeug.utils import redirect
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient()
db = client["flask-crud"]

app = Flask(__name__)


@app.route("/")
def index():
	username = request.cookies.get("username")
	if not username:
		return render_template("index.html")
	return render_template("index.html", username=username)


@app.route("/list", methods=["GET"])
def get_list():
	username = request.cookies.get("username")
	if not username:
		return redirect("/signup")

	friend_list = db.friend_list
	friends_number = friend_list.count()
	
	if friends_number > 0:
		friends = list(friend_list.find({"username": username}))
		return render_template(
			"list.html", friends=friends, username=username
			)
	return render_template("list.html", username=username)


@app.route("/list/edit/<id>", methods=["GET"])
def edit_friend(id):
	friend_list = db.friend_list
	friend = dict(friend_list.find_one({"_id": ObjectId(id)}))

	return render_template("/edit_form.html", friend=friend)


@app.route("/list/edit/<id>", methods=["POST"])
def update_friend(id):
	friend_list = db.friend_list
	friend_name = request.form["friendName"]
	social_link = request.form["socialLink"]

	if not friend_name == '' and not social_link == '':
		friend_list.find_one_and_update({"_id": ObjectId(id)}, {"$set": {
			"friend_name": friend_name,
			"social_link": social_link
		}})
	elif not friend_name == '' and social_link == '':
		friend_list.find_one_and_update({"_id": ObjectId(id)}, {"$set":{
			"friend_name": friend_name
		}})
	elif not social_link == '' and friend_name == '':
		friend_list.find_one_and_update({"_id": ObjectId(id)}, {"$set":{
			"social_link": social_link
		}})
	return redirect("/list")


@app.route("/list/delete/<id>", methods=["POST"])
def delete_friend(id):
	friend_list = db.friend_list
	friend_list.find_one_and_delete({"_id": ObjectId(id)})
	return redirect("/list")


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
		resp = make_response(redirect("/"))
		resp.set_cookie("username", username)
		return resp


@app.route("/signin", methods=["GET"])
def signin_user_view():
	return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def signin_user():
	username = request.form["username"]
	password = request.form["password"]
	errors = []
	if not username:
		errors.append({
			"error": "User or password field cannot be empty",
			"data": {
				"username": username,
				"password": password
			}
		})
		return render_template("signin.html", errors=errors)

	users = db.users
	user = dict(users.find_one({"username": username}))
	if not password == user["password"]:
		errors.append({
			"error": "User or password invalid",
			"data": {
				"username": username,
				"password": password
			}
		})
		return render_template("signin.html", errors=errors)
	resp = make_response(redirect("/"))
	resp.set_cookie("username", username)
	return resp


@app.route("/logout")
def logout():
	resp = make_response(redirect("/"))
	resp.delete_cookie("username")
	return resp