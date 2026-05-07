
from sqlalchemy import (MetaData, Table, Column, Integer, VARCHAR, DECIMAL,
                        LargeBinary, Text, ForeignKey, Date)

metadata = MetaData()

ingredientsTable = Table("ingredients", metadata,
                         Column("ingredientID", Integer, primary_key=True),
                         Column("ingredientName", VARCHAR(100), nullable=False),
                         Column("cost", DECIMAL(10, 2), nullable=False))
usersTable = Table("users", metadata,
                   Column("userID", Integer, primary_key=True),
                   Column("username", VARCHAR(50), nullable=False),
                   Column("firstName", VARCHAR(100), nullable=False),
                   Column("lastName", VARCHAR(100), nullable=False),
                   Column("password", LargeBinary, nullable=False),)
recipesTable = Table("recipes", metadata,
                     Column("recipeID", Integer, primary_key=True),
                    Column("recipeName", VARCHAR(100), nullable=False),
                    Column("img", VARCHAR(100), nullable=True),
                    Column("instructions", Text, nullable=False),
                    Column("userID", Integer, ForeignKey("users.userID"), nullable=False),
                    Column("createdDate", Date, nullable=False),)
measurementsTable = Table("measurements", metadata,
                          Column("measurement", VARCHAR(10), primary_key=True))
equipmentTable = Table("equipment", metadata,
                       Column("equipment", VARCHAR(100), primary_key=True),
                       Column("cost", DECIMAL(10, 2), nullable=False))
ingredients_n_measurementsTable = Table("ingredients_n_measurements", metadata,
                    Column("ingredientID", Integer, ForeignKey("ingredients.ingredientID"), primary_key=True),
                    Column("measurement", VARCHAR(10), ForeignKey("measurements.measurement"), primary_key=True))
recipes_n_equipmentTable = Table("recipes_n_equipment", metadata,
                                 Column("recipeID", Integer, ForeignKey("recipes.recipeID"), primary_key=True),
                                 Column("equipment", VARCHAR(100), ForeignKey("equipment.equipment"), primary_key=True))
recipes_n_ingredientsTable = Table("recipes_n_ingredients", metadata,
                                   Column("recipeID", Integer, ForeignKey("recipes.recipeID"), primary_key=True),
                                   Column("ingredientID", Integer, ForeignKey("ingredients.ingredientID"), primary_key=True),
                                   Column("amount", DECIMAL(10, 4), nullable=False),
                                   Column("measurement", VARCHAR(10), ForeignKey("measurements.measurement"),nullable=False))
recipes_n_tagsTable = Table("recipes_n_tags", metadata,
                            Column("recipeID", Integer, ForeignKey("recipes.recipeID"), primary_key=True),
                            Column("tag", VARCHAR(100), primary_key=True))
users_n_equipmentTable = Table("users_n_equipment", metadata,
                               Column("userID", Integer, ForeignKey("users.userID"), primary_key=True),
                               Column("equipment", VARCHAR(100), ForeignKey("equipment.equipment"),primary_key=True))
users_n_ingredientsTable = Table("users_n_ingredients", metadata,
                                 Column("userID", Integer, ForeignKey("users.userID"), primary_key=True),
                                 Column("ingredientID", Integer, ForeignKey("ingredients.ingredientID"), primary_key=True))
favorite_recipesTable = Table("favorite_recipes", metadata,
                              Column("userID", Integer, ForeignKey("users.userID"), primary_key=True),
                              Column("recipeID", Integer, ForeignKey("recipes.recipeID"), primary_key=True))
