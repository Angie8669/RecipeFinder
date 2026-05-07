const userID = sessionStorage.getItem('userID');
if(userID == null) {
    window.location.replace("/login");
}

$(document).ready(function() {
    let numIngredients = 0;
    let ingredients = {};

    function addIngredientDropdown() {
        numIngredients++;

        let ingredientHTML = "<select id='ingredientDropDown"+numIngredients+"'>";
        ingredientHTML += "<option value=''></option>";
        for(const ingredient of ingredients) {
            ingredientHTML += "<option value='"+ingredient.ingredientID+"'>"+ingredient.ingredientName+"</option>";
        }
        ingredientHTML += "</select>";
        ingredientHTML += "<button id='deleteIngredient"+numIngredients+"'>Delete Ingredient</button>";
        $("#ingredientList").append(ingredientHTML);
        $("#deleteIngredient"+numIngredients).on("click", function(event) {
            let i = event.target.id.replace("deleteIngredient", "");
            $("#ingredientDropDown"+i).remove()
            $("#deleteIngredient"+i).remove()
        });
    }

    $.ajax({
        url: "/api/getAllIngredients",
        method: "GET",
        dataType: "json",
        success: function (data) {
            ingredients = data;
            getIngredientList();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });
    function getIngredientList() {
        $.ajax({
            url: "/api/getIngredientList/"+userID,
            method: "GET",
            dataType: "json",
            success: function (data) {
                numIngredients = data.length;
                for(let i = 1; i <= numIngredients; i++) {
                    const val = data[i-1];

                    let ingredientHTML = "<select id='ingredientDropDown"+i+"'>";
                    ingredientHTML += "<option value=''></option>";

                    for(const ingredient of ingredients) {
                        if(ingredient.ingredientID == val.ingredientID) {
                            ingredientHTML += "<option value='"+ingredient.ingredientID+"' selected>"+ingredient.ingredientName+"</option>";
                        } else {
                            ingredientHTML += "<option value='"+ingredient.ingredientID+"'>"+ingredient.ingredientName+"</option>";
                        }
                    }

                    ingredientHTML += "</select>";
                    ingredientHTML += "<button id='deleteIngredient"+i+"'>Delete Ingredient</button>";
                    $("#ingredientList").append(ingredientHTML);
                    $("#deleteIngredient"+i).on("click", function(event) {
                        let j = event.target.id.replace("deleteIngredient", "");
                        $("#ingredientDropDown"+j).remove()
                        $("#deleteIngredient"+j).remove()
                    });
                }
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    }

    $("#addIngredient").on("click", addIngredientDropdown);


    $("#submit").on("click", function(){

       var ingredientVals = [];


       for(var i = 1; i <= numIngredients; i++) {
            if($("#ingredientDropDown"+i).length) {
                let ingredient = {};
                ingredient["ingredientID"] = $("#ingredientDropDown"+i).val();
                ingredientVals.push(ingredient);

            }
       }

       let ingredientList = {};

       ingredientList["userID"] = userID;
       ingredientList["ingredients"] = ingredientVals;
       console.log(ingredientList);

       $.ajax({
            url: "/api/updateIngredientList",
            method: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(ingredientList),
            success: function (data) {
                console.log(data);
                window.location.href="/profile";
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });


});