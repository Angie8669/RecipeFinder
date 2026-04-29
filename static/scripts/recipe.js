$(document).ready(function() {
    const path = window.location.pathname;
    const pathSegments = path.split("/");
    const recipeID = pathSegments.pop();

    recipe = {}

    function populateRecipe() {
        let html = "<div class='recipe'>";
        html += "<h1>"+recipe.recipeName+"</h1>";
        html += "<p>"+recipe.author+"</p>";
        html += "<img src='"+recipe.img+"'/>";
        html += "<div class='container'>";
        html += "<div class='column'>";
        html += "<h3>Ingredients</h3>";
        for(let ingredientID in recipe.ingredients) {
            html += "<p>" + recipe.ingredients[ingredientID].ingredientName + "</p>";
        }
        html += "</div>";
        html += "<div class='column'>";
        html += "<h3>Equipment</h3>";
        for(const equipment of recipe.equipment.split(",")) {
            html += "<p>" + equipment + "</p>";
        }
        html += "</div>";
        html += "</div>";
        html += "<h3>Instructions</h3>";
        html += "<p>"+recipe.instructions+"</p>";
        html += "</div>";

        $(".content").append(html);
    }

    $.ajax({
        url: "/api/getRecipe/"+recipeID,
        method: "GET",
        dataType: "json",
        success: function (data) {
            recipe = data;
            console.log(recipe);
            populateRecipe();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });
});