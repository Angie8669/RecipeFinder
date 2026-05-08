import sqlalchemy
from sqlalchemy import (create_engine,select, insert, delete, func)
import bcrypt
import os
from flask import request
from tables import *
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))


def initViews(app):
    @app.route("/api/getRecipe/<recipeID>")
    def getRecipe(recipeID):
        userID = request.args.get("userID")
        query = (select(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID, recipesTable.c.instructions, recipesTable.c.img, recipesTable.c.createdDate,
                        func.aggregate_strings(recipes_n_equipmentTable.c.equipment, ",").label("equipment"))
                 .select_from(recipesTable).join(recipes_n_equipmentTable, recipesTable.c.recipeID == recipes_n_equipmentTable.c.recipeID, isouter=True)
                 .where(recipesTable.c.recipeID == recipeID)
                 .group_by(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID, recipesTable.c.instructions, recipesTable.c.img, recipesTable.c.createdDate))
        recipesData = queryDatabase(query)
        if len(recipesData) == 0:
            return {}

        recipe = recipesData[0]

        query = select(usersTable).where(usersTable.c.userID == recipe["userID"])
        userData = queryDatabase(query)
        recipe["author"] = userData[0]["firstName"] + " " + userData[0]["lastName"]
        recipe["ingredients"] = {}

        query = (select(recipes_n_ingredientsTable.c.ingredientID, ingredientsTable.c.ingredientName, recipes_n_ingredientsTable.c.amount,
                        recipes_n_ingredientsTable.c.measurement)
                 .select_from(recipes_n_ingredientsTable).join(ingredientsTable, recipes_n_ingredientsTable.c.ingredientID == ingredientsTable.c.ingredientID, isouter=True).where(recipes_n_ingredientsTable.c.recipeID == recipeID))
        recipeIngredients = queryDatabase(query)
        for ingredient in recipeIngredients:
            recipe["ingredients"][ingredient["ingredientID"]] = ingredient

        if userID is not None:
            query = (select(favorite_recipesTable).where(favorite_recipesTable.c.userID == userID, favorite_recipesTable.c.recipeID == recipeID))
            favorites = queryDatabase(query)
            if len(favorites) > 0:
                recipe["favorited"] = True
            else:
                recipe["favorited"] = False
        else:
            recipe["favorited"] = False

        return recipe

    @app.route("/api/getAllIngredients")
    def getAllIngredients():
        query = (select(ingredientsTable.c.ingredientID, ingredientsTable.c.ingredientName, ingredientsTable.c.cost, func.aggregate_strings(ingredients_n_measurementsTable.c.measurement, ",").label("possibleMeasurements"))
                 .select_from(ingredientsTable).join(ingredients_n_measurementsTable, ingredientsTable.c.ingredientID == ingredients_n_measurementsTable.c.ingredientID, isouter= True)
                 .group_by(ingredientsTable.c.ingredientID, ingredientsTable.c.ingredientName, ingredientsTable.c.cost).order_by(ingredientsTable.c.ingredientName))
        response = queryDatabase(query)
        return response

    @app.route("/api/getAllEquipment")
    def getAllEquipment():
        query = select(equipmentTable)
        response = queryDatabase(query)
        return response

    @app.route("/api/getIngredientList/<userID>")
    def getIngredientList(userID):
        query = (select(users_n_ingredientsTable.c.ingredientID, users_n_ingredientsTable.c.userID, ingredientsTable.c.ingredientName)
                 .select_from(users_n_ingredientsTable).join(ingredientsTable, users_n_ingredientsTable.c.ingredientID == ingredientsTable.c.ingredientID, isouter= True)
                 .where(users_n_ingredientsTable.c.userID == userID))
        response = queryDatabase(query)
        return response

    @app.route("/api/getEquipmentList/<userID>")
    def getEquipmentList(userID):
        query = select(users_n_equipmentTable).where(users_n_equipmentTable.c.userID == userID)
        response = queryDatabase(query)
        return response

    @app.route("/createUser", methods=["POST"])
    def createUser():
        # Check if username exists
        username = request.json["username"]
        query = select(usersTable).where(usersTable.c.username == username)
        response = queryDatabase(query)
        if len(response) > 0:
            return "Username already exists.", 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.json["password"].encode(), salt)
        query = insert(usersTable).values({"username": username, "password": hashed_password, "firstName": request.json["firstName"], "lastName": request.json["lastName"]})
        response = queryDatabaseInsert(query)

        return "{\"response\":\"success\"}"

    @app.route("/authenticate")
    def authenticate():
        username = request.args.get("username")
        query = select(usersTable).where(usersTable.c.username == username)
        response = queryDatabase(query)
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

        query = select(usersTable).where(usersTable.c.userID == userID)
        response = queryDatabase(query)
        if len(response) == 0:
            return "User does not exist.", 400

        if instructions == "" or instructions == None:
            return "Invalid Instructions.", 400

        if len(ingredients) == 0 or ingredients == None:
            return "Invalid Ingredients.", 400

        query = insert(recipesTable).values({"recipeName": recipeName, "instructions": instructions, "img": imageURL, "userID": userID})
        recipeID = queryDatabaseInsert(query)[0]

        if not recipeID:
            return "Unable to insert recipe.", 400

        for ingredient in ingredients:
            measurement = ingredient["measurement"] if ingredient["measurement"] != "" else None
            query = insert(recipes_n_ingredientsTable).values(
                {"recipeID": recipeID, "ingredientID": ingredient["ingredientID"], "measurement": measurement, "amount": ingredient["amount"]})
            queryDatabaseInsert(query)

        for equipmentVal in equipment:
            query = insert(recipes_n_equipmentTable).values({"recipeID": recipeID, "equipment": equipmentVal})
            queryDatabaseInsert(query)

        for tag in tags.split(","):
            tag = tag.lower().strip()
            query = insert(recipes_n_tagsTable).values({"recipeID": recipeID, "tag": tag})
            queryDatabaseInsert(query)

        response = {
            "recipeID": recipeID,
            "response": "success",
        }

        return response

    @app.route("/api/updateIngredientList", methods=["POST"])
    def updateIngredientList():
        userID = request.json["userID"]
        ingredients = request.json["ingredients"]


        query = select(usersTable).where(usersTable.c.userID == userID)
        response = queryDatabase(query)
        if len(response) == 0:
            return "User does not exist.", 400

        if ingredients == None:
            ingredients = {}

        query = select(users_n_ingredientsTable).where(users_n_ingredientsTable.c.userID == userID)
        ingredientList = queryDatabase(query)
        ingredientIDList = []

        for ingredient in ingredientList:
            ingredientIDList.append(ingredient["ingredientID"])

        for newIngredient in ingredients:
            if not(int(newIngredient["ingredientID"]) in ingredientIDList):
                query = insert(users_n_ingredientsTable).values({"userID": userID, "ingredientID": newIngredient["ingredientID"]})
                queryDatabaseInsert(query)

        newIngredientIDList = []

        for ingredient in ingredients:
            newIngredientIDList.append(int(ingredient["ingredientID"]))

        for ingredientID in ingredientIDList:
            if not (int(ingredientID) in newIngredientIDList):
                query = delete(users_n_ingredientsTable).where(
                    users_n_ingredientsTable.c.userID == userID, users_n_ingredientsTable.c.ingredientID == ingredientID)
                queryDatabaseInsert(query)

        return "{\"response\":\"success\"}"

    @app.route("/api/updateEquipmentList", methods=["POST"])
    def updateEquipmentList():
        userID = request.json["userID"]
        equipment = request.json["equipment"]

        query = select(usersTable).where(usersTable.c.userID == userID)
        response = queryDatabase(query)
        if len(response) == 0:
            return "User does not exist.", 400

        if equipment == None:
            equipment = []

        query = select(users_n_equipmentTable).where(users_n_equipmentTable.c.userID == userID)
        equipmentData = queryDatabase(query)
        equipmentList = []

        for equipmentVal in equipmentData:
            equipmentList.append(equipmentVal["equipment"])

        for equipmentVal in equipment:
            if not equipmentVal in equipmentList:
                query = insert(users_n_equipmentTable).values({"userID": userID, "equipment": equipmentVal})
                queryDatabaseInsert(query)

        newEquipmentList = []

        for equipmentVal in equipment:
            newEquipmentList.append(equipmentVal)

        for equipmentVal in equipmentList:
            if not (equipmentVal in newEquipmentList):
                query = delete(users_n_equipmentTable).where(
                    users_n_equipmentTable.c.userID == userID,
                    users_n_equipmentTable.c.equipment == equipmentVal)
                queryDatabaseInsert(query)

        return "{\"response\":\"success\"}"

    @app.route("/api/getRecipes")
    def getRecipes():
        recipeName = request.args.get("recipeName") if request.args.get("recipeName") != None else ""
        userID = request.args.get("userID")
        costMin = float(request.args.get("costMin")) if request.args.get("costMin") != None else 0
        costMax = float(request.args.get("costMax")) if request.args.get("costMax") != None else float("inf")
        tags = request.args.get("tags") if request.args.get("tags") != None else ""

        recipeQuery = select(recipesTable.c.recipeID).filter(recipesTable.c.recipeName.like("%" + recipeName + "%"))
        tagsQuery = select(recipes_n_tagsTable.c.recipeID, func.aggregate_strings(recipes_n_tagsTable.c.tag, ",").label("tags")).filter(recipes_n_tagsTable.c.recipeID.in_(recipeQuery)).group_by(recipes_n_tagsTable.c.recipeID).subquery()
        equipmentQuery = select(recipes_n_equipmentTable.c.recipeID, func.aggregate_strings(recipes_n_equipmentTable.c.equipment, ",").label("equipment")).filter(recipes_n_equipmentTable.c.recipeID.in_(recipeQuery)).group_by(recipes_n_equipmentTable.c.recipeID).subquery()
        query = (select(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID,
                        recipesTable.c.instructions, recipesTable.c.img, recipesTable.c.createdDate, tagsQuery.c.tags, equipmentQuery.c.equipment)
                 .select_from(recipesTable).join(equipmentQuery, recipesTable.c.recipeID == equipmentQuery.c.recipeID,isouter=True)
                 .join(tagsQuery, recipesTable.c.recipeID == tagsQuery.c.recipeID,isouter=True).filter(recipesTable.c.recipeName.like("%" + recipeName + "%")))

        recipesData = queryDatabase(query)
        if len(recipesData) == 0:
            return {}

        recipes = {}
        for recipe in recipesData:
            query = select(usersTable).where(usersTable.c.userID == recipe["userID"])
            userData = queryDatabase(query)
            recipe["author"] = userData[0]["firstName"] + " " + userData[0]["lastName"]
            recipe["ingredients"] = {}
            recipes[recipe["recipeID"]] = recipe

        subquery = select(recipesTable.c.recipeID).filter(recipesTable.c.recipeName.like("%" + recipeName + "%"))
        query = select(recipes_n_ingredientsTable).filter(recipes_n_ingredientsTable.c.recipeID.in_(subquery))
        recipeIngredients = queryDatabase(query)
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

        query = select(ingredientsTable)
        ingredientsData = queryDatabase(query)
        ingredients = {}
        for ingredient in ingredientsData:
            ingredients[ingredient["ingredientID"]] = ingredient

        if userID != None:
            query = select(users_n_ingredientsTable).where(users_n_ingredientsTable.c.userID == userID)
            userIngredientData = queryDatabase(query)
            userIngredients = {}
            for ingredient in userIngredientData:
                userIngredients[ingredient["ingredientID"]] = ingredient

        query = select(equipmentTable)
        equipmentData = queryDatabase(query)
        equipmentDict = {}
        for equipmentVal in equipmentData:
            equipmentDict[equipmentVal["equipment"]] = equipmentVal

        if userID != None:
            query = select(users_n_equipmentTable).where(users_n_equipmentTable.c.userID == userID)
            userEquipmentData = queryDatabase(query)
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
                for ingredient in userIngredients.values():
                    if ingredient["ingredientID"] in recipe["ingredients"]:
                        userCost -= ingredients[ingredient["ingredientID"]]["cost"]
                recipe["userCost"] = userCost
                if userCost > costMax or userCost < costMin:
                    recipes.pop(recipe["recipeID"])

            else:
                if cost > costMax or cost < costMin:
                    recipes.pop(recipe["recipeID"])

            equipmentCost = 0
            recipeEquipment = recipe["equipment"].split(",") if recipe["equipment"] is not None else []
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

    @app.route("/api/getRecipesByUser/<userID>")
    def getRecipesByUser(userID):
        query = (select(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID,
                        recipesTable.c.img, recipesTable.c.createdDate,
                        func.aggregate_strings(recipes_n_equipmentTable.c.equipment, ",").label("equipment"),
                        func.aggregate_strings(recipes_n_tagsTable.c.tag, ",").label("tags"))
                 .select_from(recipesTable).join(recipes_n_equipmentTable,
                                                 recipesTable.c.recipeID == recipes_n_equipmentTable.c.recipeID,
                                                 isouter=True)
                 .join(recipes_n_tagsTable, recipesTable.c.recipeID == recipes_n_tagsTable.c.recipeID, isouter=True)
                 .where(recipesTable.c.userID == userID)
                 .group_by(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID,
                           recipesTable.c.instructions, recipesTable.c.img, recipesTable.c.createdDate))
        recipesData = queryDatabase(query)
        if len(recipesData) == 0:
            return {}

        recipes = {}
        for recipe in recipesData:
            recipe["ingredients"] = {}
            recipes[recipe["recipeID"]] = recipe

        subquery = select(recipesTable.c.recipeID).where(recipesTable.c.userID == userID)
        query = select(recipes_n_ingredientsTable).filter(recipes_n_ingredientsTable.c.recipeID.in_(subquery))
        recipeIngredients = queryDatabase(query)
        for ingredient in recipeIngredients:
            recipes[ingredient["recipeID"]]["ingredients"][ingredient["ingredientID"]] = ingredient

        query = select(ingredientsTable)
        ingredientsData = queryDatabase(query)
        ingredients = {}
        for ingredient in ingredientsData:
            ingredients[ingredient["ingredientID"]] = ingredient

        if userID != None:
            query = select(users_n_ingredientsTable).where(users_n_ingredientsTable.c.userID == userID)
            userIngredientData = queryDatabase(query)
            userIngredients = {}
            for ingredient in userIngredientData:
                userIngredients[ingredient["ingredientID"]] = ingredient

        query = select(equipmentTable)
        equipmentData = queryDatabase(query)
        equipmentDict = {}
        for equipmentVal in equipmentData:
            equipmentDict[equipmentVal["equipment"]] = equipmentVal

        if userID != None:
            query = select(users_n_equipmentTable).where(users_n_equipmentTable.c.userID == userID)
            userEquipmentData = queryDatabase(query)
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
                for ingredient in userIngredients.values():
                    if ingredient["ingredientID"] in recipe["ingredients"]:
                        userCost -= ingredients[ingredient["ingredientID"]]["cost"]
                recipe["userCost"] = userCost


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

    @app.route("/api/getFavoriteRecipes/<userID>")
    def getFavoriteRecipes(userID):
        subquery = select(favorite_recipesTable.c.recipeID).where(favorite_recipesTable.c.userID == userID)
        query = (select(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID,
                        recipesTable.c.img, recipesTable.c.createdDate,
                        func.aggregate_strings(recipes_n_equipmentTable.c.equipment, ",").label("equipment"),
                        func.aggregate_strings(recipes_n_tagsTable.c.tag, ",").label("tags"))
                 .select_from(recipesTable).join(recipes_n_equipmentTable,
                                                 recipesTable.c.recipeID == recipes_n_equipmentTable.c.recipeID,
                                                 isouter=True)
                 .join(recipes_n_tagsTable, recipesTable.c.recipeID == recipes_n_tagsTable.c.recipeID, isouter=True)
                 .filter(recipesTable.c.recipeID.in_(subquery))
                 .group_by(recipesTable.c.recipeID, recipesTable.c.recipeName, recipesTable.c.userID,
                           recipesTable.c.instructions, recipesTable.c.img, recipesTable.c.createdDate))
        recipesData = queryDatabase(query)
        if len(recipesData) == 0:
            return {}

        recipes = {}
        for recipe in recipesData:
            recipe["ingredients"] = {}
            recipes[recipe["recipeID"]] = recipe

        subquery2 = select(recipesTable.c.recipeID).filter(recipesTable.c.recipeID.in_(subquery))
        query = select(recipes_n_ingredientsTable).filter(recipes_n_ingredientsTable.c.recipeID.in_(subquery2))
        recipeIngredients = queryDatabase(query)
        for ingredient in recipeIngredients:
            recipes[ingredient["recipeID"]]["ingredients"][ingredient["ingredientID"]] = ingredient

        query = select(ingredientsTable)
        ingredientsData = queryDatabase(query)
        ingredients = {}
        for ingredient in ingredientsData:
            ingredients[ingredient["ingredientID"]] = ingredient

        if userID != None:
            query = select(users_n_ingredientsTable).where(users_n_ingredientsTable.c.userID == userID)
            userIngredientData = queryDatabase(query)
            userIngredients = {}
            for ingredient in userIngredientData:
                userIngredients[ingredient["ingredientID"]] = ingredient

        query = select(equipmentTable)
        equipmentData = queryDatabase(query)
        equipmentDict = {}
        for equipmentVal in equipmentData:
            equipmentDict[equipmentVal["equipment"]] = equipmentVal

        if userID != None:
            query = select(users_n_equipmentTable).where(users_n_equipmentTable.c.userID == userID)
            userEquipmentData = queryDatabase(query)
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
                for ingredient in userIngredients.values():
                    if ingredient["ingredientID"] in recipe["ingredients"]:
                        userCost -= ingredients[ingredient["ingredientID"]]["cost"]
                recipe["userCost"] = userCost

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

    @app.route("/api/setFavorite", methods=["POST"])
    def setFavorite():
        userID = request.json["userID"]
        recipeID = request.json["recipeID"]
        query = insert(favorite_recipesTable).values({"userID": userID, "recipeID": recipeID})
        queryDatabaseInsert(query)

        return "{\"response\":\"success\"}"

    @app.route("/api/setUnfavorite", methods=["POST"])
    def setUnfavorite():
        userID = request.json["userID"]
        recipeID = request.json["recipeID"]

        query = delete(favorite_recipesTable).where(favorite_recipesTable.c.userID == userID, favorite_recipesTable.c.recipeID == recipeID)
        queryDatabaseInsert(query)

        return "{\"response\":\"success\"}"

def queryDatabase(statement):
    response = []
    with engine.connect() as connection:
        for row in connection.execute(statement):
            response.append(dict(row._mapping))

    return response

def queryDatabaseInsert(statement):
    result = {}
    with engine.connect() as connection:
        result = connection.execute(statement)
        connection.commit()

    if isinstance(statement, sqlalchemy.sql.expression.Delete):
        return
    return result.inserted_primary_key