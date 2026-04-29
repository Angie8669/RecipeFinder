from asyncio.windows_events import NULL

import bcrypt
import credentials
import pyodbc
from flask import request


def initViews(app):

    @app.route("/api/getRecipe/<recipeID>")
    def getRecipe(recipeID):
        query = "SELECT r.recipeID, recipeName, userID, instructions, img, createdDate, STUFF((SELECT ','+equipment FROM recipes_n_equipment rne WHERE r.recipeID = rne.recipeID FOR xml path('')),1,1,'') as equipment FROM recipes r WHERE recipeID = ?"
        data = (recipeID)
        recipesData = queryDatabase(query, data)
        if len(recipesData) == 0:
            return {}

        recipe = recipesData[0]

        query = "SELECT * FROM users WHERE userID = ?"
        data = (recipe["userID"])
        userData = queryDatabase(query, data)
        recipe["author"] = userData[0]["firstName"] + " " + userData[0]["lastName"]
        recipe["ingredients"] = {}

        query = "SELECT rni.ingredientID, i.ingredientName, rni.amount, rni.measurement FROM recipes_n_ingredients rni LEFT JOIN ingredients i ON rni.ingredientID = i.ingredientID WHERE recipeID = ?"
        data = (recipeID)
        recipeIngredients = queryDatabase(query, data)
        for ingredient in recipeIngredients:
            recipe["ingredients"][ingredient["ingredientID"]] = ingredient

        return recipe

    @app.route("/api/getAllIngredients")
    def getAllIngredients():
        query = "SELECT i.ingredientID, ingredientName, cost, STRING_AGG(CONVERT(NVARCHAR(max), inm.measurement), ',') as possibleMeasurements FROM ingredients i LEFT JOIN ingredients_n_measurements inm ON i.ingredientID = inm.ingredientID group by i.ingredientID, ingredientName, cost ORDER BY i.ingredientName"
        response = queryDatabase(query)
        return response

    @app.route("/api/getAllEquipment")
    def getAllEquipment():
        query = "SELECT * FROM equipment"
        response = queryDatabase(query)
        return response

    @app.route("/api/getIngredientList/<userID>")
    def getIngredientList(userID):
        query = "SELECT * FROM users_n_ingredients WHERE userID = ?"
        data = (userID)
        response = queryDatabase(query, data)
        return response

    @app.route("/api/getEquipmentList/<userID>")
    def getEquipmentList(userID):
        query = "SELECT * FROM users_n_equipment WHERE userID = ?"
        data = (userID)
        response = queryDatabase(query, data)
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
        print(response)
        if len(response) == 0:
            return "Incorrect Username or Password.", 400

        if bcrypt.checkpw(request.args.get("password").encode(), response[0]["password"]):
            user = {"userID": response[0]["userID"], "username": response[0]["username"]}
            return user
        else:
            return "Incorrect Username or Password.", 400

    @app.route("/api/createRecipe", methods=["POST"])
    def createRecipe():
        userID = request.json["userID"]
        recipeName = request.json["recipeName"]
        imageURL = request.json["imageURL"]
        instructions = request.json["instructions"]
        ingredients = request.json["ingredients"]
        equipment = request.json["equipment"]
        tags = request.json["tags"]

        query = "SELECT * FROM users WHERE userID = ?"
        data = (userID)
        response = queryDatabase(query, data)
        if len(response) == 0:
            return "User does not exist.", 400

        if instructions == "" or instructions == None:
            return "Invalid Instructions.", 400

        if len(ingredients) == 0 or ingredients == None:
            return "Invalid Ingredients.", 400

        query = "INSERT INTO recipes (recipeName, instructions, img, userID) VALUES (?, ?, ?, ?)"
        data = (recipeName, instructions, imageURL, userID)
        recipeID = queryDatabaseInsert(query, data)

        if not recipeID:
            return "Unable to insert recipe.", 400

        for ingredient in ingredients:
            measurement = ingredient["measurement"] if ingredient["measurement"] != "" else None
            query = "INSERT INTO recipes_n_ingredients (recipeID, ingredientID, measurement, amount) VALUES (?, ?, ?, ?)"
            data = (recipeID, ingredient["ingredientID"], measurement, ingredient["amount"])
            queryDatabaseInsert(query, data)

        for equipmentVal in equipment:
            query = "INSERT INTO recipes_n_equipment (recipeID, equipment) VALUES (?, ?)"
            data = (recipeID, equipmentVal)
            queryDatabaseInsert(query, data)

        for tag in tags.split(","):
            tag = tag.lower().strip()
            query = "INSERT INTO recipes_n_tags (recipeID, tag) VALUES (?, ?)"
            data = (recipeID, tag)
            queryDatabaseInsert(query, data)

        response = {
            "recipeID": recipeID,
            "response": "success",
        }

        return response

    @app.route("/api/updateIngredientList", methods=["POST"])
    def updateIngredientList():
        userID = request.json["userID"]
        ingredients = request.json["ingredients"]


        query = "SELECT * FROM users WHERE userID = ?"
        data = (userID)
        response = queryDatabase(query, data)
        if len(response) == 0:
            return "User does not exist.", 400

        if len(ingredients) == 0 or ingredients == None:
            return "Invalid Ingredients.", 400

        query = "SELECT * FROM users_n_ingredients WHERE userID = ?"
        data = (userID)
        ingredientList = queryDatabase(query, data)


        for newIngredient in ingredients:
            measurement = newIngredient["measurement"] if newIngredient["measurement"] != "" else None
            updated = False
            for oldIngredient in ingredientList:
                if int(newIngredient["ingredientID"]) == int(oldIngredient["ingredientID"]):
                    updated = True
                    query = "UPDATE users_n_ingredients SET amount = ?, measurement = ? WHERE userID = ? AND ingredientID = ?"
                    data = (newIngredient["amount"], measurement, userID, newIngredient["ingredientID"])
                    queryDatabaseInsert(query, data)
                    break

            if not updated:
                query = "INSERT INTO users_n_ingredients (userID, ingredientID, measurement, amount) VALUES (?, ?, ?, ?)"
                data = (userID, newIngredient["ingredientID"], measurement, newIngredient["amount"])
                queryDatabaseInsert(query, data)


        return "{\"response\":\"success\"}"

    @app.route("/api/updateEquipmentList", methods=["POST"])
    def updateEquipmentList():
        userID = request.json["userID"]
        equipment = request.json["equipment"]

        query = "SELECT * FROM users WHERE userID = ?"
        data = (userID)
        response = queryDatabase(query, data)
        if len(response) == 0:
            return "User does not exist.", 400

        if len(equipment) == 0 or equipment == None:
            return "Invalid equipment.", 400

        query = "SELECT * FROM users_n_equipment WHERE userID = ?"
        data = (userID)
        equipmentData = queryDatabase(query, data)
        equipmentList = []

        for equipmentVal in equipmentData:
            equipmentList.append(equipmentVal["equipment"])

        for equipmentVal in equipment:
            if not equipmentVal in equipmentList:
                query = "INSERT INTO users_n_equipment (userID, equipment) VALUES (?, ?)"
                data = (userID, equipmentVal)
                queryDatabaseInsert(query, data)

        return "{\"response\":\"success\"}"

    @app.route("/api/getRecipes")
    def getRecipes():
        recipeName = request.args.get("recipeName") if request.args.get("recipeName") != None else ""
        userID = request.args.get("userID")
        costMin = float(request.args.get("costMin")) if request.args.get("costMin") != None else 0
        costMax = float(request.args.get("costMax")) if request.args.get("costMax") != None else float("inf")
        tags = request.args.get("tags") if request.args.get("tags") != None else ""

        query = "SELECT r.recipeID, recipeName, userID, instructions, img, createdDate, STUFF((SELECT ','+equipment FROM recipes_n_equipment rne WHERE r.recipeID = rne.recipeID FOR xml path('')),1,1,'') as equipment, STUFF((SELECT ','+tag FROM recipes_n_tags rnt WHERE r.recipeID = rnt.recipeID FOR xml path('')),1,1,'') as tags FROM recipes r WHERE recipeName LIKE ?"
        data = ('%' + recipeName + '%')
        recipesData = queryDatabase(query, data)
        if len(recipesData) == 0:
            return {}

        recipes = {}
        for recipe in recipesData:
            query = "SELECT * FROM users WHERE userID = ?"
            data = (recipe["userID"])
            userData = queryDatabase(query, data)
            recipe["author"] = userData[0]["firstName"] + " " + userData[0]["lastName"]
            recipe["ingredients"] = {}
            recipes[recipe["recipeID"]] = recipe

        query = "SELECT * FROM recipes_n_ingredients WHERE recipeID IN (SELECT recipeID FROM recipes WHERE recipeName LIKE ?)"
        data = ('%' + recipeName + '%')
        recipeIngredients = queryDatabase(query, data)
        for ingredient in recipeIngredients:
            recipes[ingredient["recipeID"]]["ingredients"][ingredient["ingredientID"]] = ingredient

        if tags != "":
            for recipe in list(recipes.values()):
                keep = False
                for tag in tags.split(","):
                    tag = tag.lower().strip()
                    if recipe["tags"] is not None and tag in recipe["tags"]:
                        keep = True
                        break
                if not keep:
                    recipes.pop(recipe["recipeID"])

        query = "SELECT * FROM ingredients"
        data = ()
        ingredientsData = queryDatabase(query, data)
        ingredients = {}
        for ingredient in ingredientsData:
            ingredients[ingredient["ingredientID"]] = ingredient

        if userID != None:
            query = "SELECT * FROM users_n_ingredients WHERE userID = ?"
            data = (userID)
            userIngredientData = queryDatabase(query, data)
            userIngredients = {}
            for ingredient in userIngredientData:
                userIngredients[ingredient["ingredientID"]] = ingredient

        query = "SELECT * FROM equipment"
        data = ()
        equipmentData = queryDatabase(query, data)
        equipmentDict = {}
        for equipmentVal in equipmentData:
            equipmentDict[equipmentVal["equipment"]] = equipmentVal

        if userID != None:
            query = "SELECT * FROM users_n_equipment WHERE userID = ?"
            data = (userID)
            userEquipmentData = queryDatabase(query, data)
            userEquipment = {}
            for equipmentVal in userEquipmentData:
                userEquipment[equipmentVal["equipment"]] = equipmentVal


        for recipe in list(recipes.values()):
            cost = 0
            for ingredientID in recipe["ingredients"]:
                cost += ingredients[ingredientID]["cost"]

            recipe["cost"] = cost
            if userID != None:
                userCost = cost
                print(recipe["ingredients"])
                for ingredient in userIngredients.values():
                    print(ingredient["ingredientID"])
                    if ingredient["ingredientID"] in recipe["ingredients"]:
                        userCost -= ingredients[ingredient["ingredientID"]]["cost"]
                recipe["userCost"] = userCost
                print(userCost, costMax, costMin)
                if userCost > costMax or userCost < costMin:
                    recipes.pop(recipe["recipeID"])

            else:
                if cost > costMax or cost < costMin:
                    recipes.pop(recipe["recipeID"])

            equipmentCost = 0
            recipeEquipment = recipe["equipment"].split(",")
            for equipment in recipeEquipment:
                equipmentCost += equipmentDict[equipment]["cost"]

            recipe["equipmentCost"] = equipmentCost
            if userID != None:
                userEquipmentCost = equipmentCost
                for equipment in userEquipment:
                    if equipment in recipeEquipment:
                        userEquipmentCost -= equipmentDict[equipment]["cost"]
                recipe["userEquipmentCost"] = userEquipmentCost

        return recipes



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
        insertID = cur.execute("SELECT @@IDENTITY AS id;").fetchone()[0]
        conn.commit()
        cur.close()
        return insertID
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()