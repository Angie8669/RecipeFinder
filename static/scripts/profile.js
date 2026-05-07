const userID = sessionStorage.getItem('userID');

$(document).ready(function() {
    let recipes = {};
    let favorites = {};
    let currentDisplay = "recipes";
    let ingredients = [];
    let equipment = [];

    function showRecipes() {
        let html = "";
        for(let recipeID in recipes) {
            let recipe = recipes[recipeID];
            html += "<div class='row'>";
            html += "<a href='/recipe/"+recipeID+"'>";
            html += "<img class='img' src='"+recipe.img+"'/>";
            html += "<span>"+recipe.recipeName+"</span>";
            html += "<span>"+recipe.userCost+"</span>";
            html += "<span>"+recipe.equipmentCost+"</span>";
            html += "</a>"
            html += "</div>";
        }
        $(".currentDisplay").empty();
        $(".currentDisplay").append(html);
    }

    function showFavorites() {
        let html = "";
        for(let recipeID in favorites) {
            let recipe = favorites[recipeID];
            html += "<div class='row'>";
            html += "<a href='/recipe/"+recipeID+"'>";
            html += "<img class='img' src='"+recipe.img+"'/>";
            html += "<span>"+recipe.recipeName+"</span>";
            html += "<span>"+recipe.userCost+"</span>";
            html += "<span>"+recipe.equipmentCost+"</span>";
            html += "</a>"
            html += "</div>";
        }
        $(".currentDisplay").empty();
        $(".currentDisplay").append(html);
    }

    function swapDisplay() {
        if(currentDisplay == "recipes") {
            showFavorites();
            currentDisplay = "favorites";
            $("#swapDisplayButton").html("Show Recipes");
        } else {
            showRecipes();
            currentDisplay = "recipes";
            $("#swapDisplayButton").html("Show Favorites");
        }
    }

    function displayIngredients() {
        let html = "<h3>Ingredients</h3>";
        for(let ingredient of ingredients) {
            html += "<p>"+ingredient.ingredientName+"</p>";
        }
        $("#ingredientList").append(html);
    }

    function displayEquipment() {
        let html = "<h3>Equipment</h3>";
        for(let equipmentVal of equipment) {
            html += "<p>"+equipmentVal.equipment+"</p>";
        }
        $("#equipmentList").append(html);
    }

    $("#swapDisplayButton").on("click", swapDisplay);

    $.ajax({
        url: "/api/getRecipesByUser/"+userID,
        method: "GET",
        dataType: "json",
        success: function (data) {
            recipes = data;
            showRecipes();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });
    $.ajax({
        url: "/api/getFavoriteRecipes/"+userID,
        method: "GET",
        dataType: "json",
        success: function (data) {
            favorites = data;
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $.ajax({
        url: "/api/getIngredientList/"+userID,
        method: "GET",
        dataType: "json",
        success: function (data) {
            ingredients = data;
            displayIngredients();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });
    $.ajax({
        url: "/api/getEquipmentList/"+userID,
        method: "GET",
        dataType: "json",
        success: function (data) {
            equipment = data;
            displayEquipment();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });
});