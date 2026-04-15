import bcrypt
import credentials
import pyodbc
from flask import request


def initViews(app):
    @app.route("/api/getAllIngredients")
    def getAllIngredients():
        query = "SELECT * FROM ingredients"
        response = queryDatabase(query)
        return response

    @app.route("/api/getAllEquipment")
    def getAllEquipment():
        query = "SELECT * FROM equipment"
        response = queryDatabase(query)
        return response

    @app.route("/createUser", methods=["POST"])
    def createUser():
        # Check if username exists
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

    @app.route("/authenticate")
    def authenticate():
        username = request.args.get("username")
        query = "SELECT * FROM users WHERE username = ?"
        data = (username)
        response = queryDatabase(query, data)
        if len(response) == 0:
            return "Incorrect Username or Password.", 400

        if bcrypt.checkpw(request.args.get("password").encode(), response[0].password):
            return f"{{\"userID\":{response[0].userID}}}"
        else:
            return "Incorrect Username or Password.", 400


password = credentials.password

def queryDatabase(query, data=[]):
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
        rows = cur.fetchall()
        columns = [column[0] for column in cur.description]
        response = []

        for row in rows:
            data = {}
            for i in range(len(columns)):
                data[columns[i]] = row[i]
            response.append(data)

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