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

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/ingredientListForm")
def ingredientListForm():
    return render_template("ingredientListForm.html")

@app.route("/equipmentListForm")
def equipmentListForm():
    return render_template("equipmentListForm.html")

@app.route("/recipes")
def recipes():
    return render_template("recipes.html")

@app.route("/recipe/<recipeID>")
def recipe(recipeID):
    return render_template("recipe.html")


if __name__ == "__main__":
    app.run(debug=False)