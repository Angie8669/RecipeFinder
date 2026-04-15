from flask import Flask, render_template
from API_Routes import initViews

app = Flask(__name__)
initViews(app)

@app.route("/")
def start_index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signUp.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/recipeForm")
def recipeForm():
    return render_template("recipeForm.html")



app.run(host="0.0.0.0", port=5000)