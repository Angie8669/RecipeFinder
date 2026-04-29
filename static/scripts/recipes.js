const userID = sessionStorage.getItem('userID');

$(document).ready(function() {
    let url = "/api/getRecipes";
    if (userID != null) {
        url += "?userID=" + userID;
    }
    let recipes = [];

    function populateRecipes() {
        $("#recipeList").empty();
        let html = "";
        if(jQuery.isEmptyObject(recipes)) {
            html += "<p>Your search filters returned no recipe results. Try changing your search criteria.</p>"
        } else {
            for(let recipeID in recipes) {
                recipe = recipes[recipeID];
                html += "<div class='recipe'>";
                html += "<img src='"+recipe.img+"'/>";
                html += "<h3>"+recipe.recipeName+"</h3>";
                html += "<p>"+recipe.author+"</p>";
                html += "<p>Base Cost: $"+recipe.cost+"</p>";
                if(recipe.userCost != null) {
                    html += "<p>User Cost: $"+recipe.userCost+"</p>";
                }
                html += "<p>Base Equipment Cost: $"+recipe.equipmentCost+"</p>";
                if(recipe.userEquipmentCost != null) {
                    html += "<p>User Equipment Cost: $"+recipe.userEquipmentCost+"</p>";
                }
                html += "</div>";
            }
        }
        $("#recipeList").append(html);
    }

    $.ajax({
        url: url,
        method: "GET",
        dataType: "json",
        success: function (data) {
            recipes = data;
            console.log(recipes);
            populateRecipes();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $("#search").on("click", function() {
        var recipeName = $("#recipeName").val();
        var tags = $("#tags").val();
        var min = $("#min").val();
        var max = $("#max").val();

        let url = "/api/getRecipes?recipeName="+recipeName;

        if(userID != null) {
            url += "&userID="+userID;
        }
        if(min != "") {
            url += "&costMin="+min;
        }
        if(max != "") {
            url += "&costMax="+max;
        }

        $.ajax({
            url: url,
            method: "GET",
            dataType: "json",
            success: function (data) {
                recipes = data;
                console.log(recipes);
                populateRecipes();
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });
});