from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route("/")
def index():
	url_for("static", filename="style.css")
	return render_template("index.html")


@app.route("/list")
def get_list():
	url_for("static", filename="style.css")
	return render_template("list.html")