from flask import Flask, render_template, request
import credentials
import pyodbc
import boto3
import bcrypt

password = credentials.password

def queryDatabase(query, data):
    conn = None
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=recipefinder.cx6i4gwoqz8e.us-east-2.rds.amazonaws.com,1433;"
            "DATABASE=RecipeFinder;"
            "UID=admin;"
            "PWD=" + (password) + ";"
            "Encrypt=yes;TrustServerCertificate=yes;"
        )
        cur = conn.cursor()
        cur.execute(query, data)
        #print(cur.fetchone()[0])
        response = cur.fetchall()
        cur.close()
        return response
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def queryDatabaseInsert(query, data):
    conn = None
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=recipefinder.cx6i4gwoqz8e.us-east-2.rds.amazonaws.com,1433;"
            "DATABASE=RecipeFinder;"
            "UID=admin;"
            "PWD=" + (password) + ";"
            "Encrypt=yes;TrustServerCertificate=yes;"
        )
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

app = Flask(__name__)

@app.route("/")
def start_index():
    return render_template("index.html")

@app.route("/test")
def test():
    response = queryDatabase('SELECT @@VERSION')
    rows = []
    for row in response:
        rows.append(row)
        print(row)
    return rows

@app.route("/signup")
def signup():
    return render_template("signUp.html")

@app.route("/createUser", methods=["POST"])
def createUser():
    #Check if username exists
    username = request.json["username"]
    query = "SELECT * FROM users WHERE username = ?"
    data = (username)
    response = queryDatabase(query, data)
    if len(response) > 0:
        return "Username already exists.", 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.json["password"].encode(), salt)
    query = "INSERT INTO users (firstName, lastName, username, password) VALUES (?, ?, ?, ?)"
    data = (request.json["firstName"], request.json["lastName"], username, hashed_password)
    response = queryDatabaseInsert(query, data)


    return "{\"response\":\"success\"}"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate")
def authenticate():
    username = request.args.get("username")
    query = "SELECT * FROM users WHERE username = ?"
    data = (username)
    response = queryDatabase(query, data)
    print(response[0])
    print(type(response[0]))
    if len(response) == 0:
        return "Incorrect Username or Password.", 400

    if bcrypt.checkpw(request.args.get("password").encode(), response[0].password):
        return f"{{\"userID\":{response[0].userID}}}"
    else:
        return "Incorrect Username or Password.", 400





app.run(host="0.0.0.0", port=5000)