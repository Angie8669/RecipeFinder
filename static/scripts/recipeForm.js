const userID = sessionStorage.getItem('userID');
if(userID == null) {
    window.location.replace("/login");
}

$(document).ready(function() {
    let numIngredients = 0;
    let ingredients = {};

    function addIngredientDropdown() {
        numIngredients++;

        let ingredientHTML = "<input type='number' step='0.0625' id='amount"+numIngredients+"'/>"
        ingredientHTML += "<select id='measurementDropDown"+numIngredients+"'>";
        ingredientHTML += "<option value=''></option>";

        ingredientHTML += "</select>";
        ingredientHTML += "<select id='ingredientDropDown"+numIngredients+"'>";
        ingredientHTML += "<option value=''></option>";
        for(const ingredient of ingredients) {
            ingredientHTML += "<option value='"+ingredient.ingredientID+"'>"+ingredient.ingredientName+"</option>";
        }
        ingredientHTML += "</select>";
        $("#ingredientList").append(ingredientHTML);

        $("#ingredientDropDown"+numIngredients).on("change", function(event){

            let i = event.target.id.replace("ingredientDropDown", "");
            console.log(i)
            let curVal = $("#ingredientDropDown"+i).val();
            for(const ingredient of ingredients) {
                if(ingredient.ingredientID == curVal) {
                    const measurements = ingredient.possibleMeasurements.split(",");
                    console.log(measurements);
                    $("#measurementDropDown"+i).empty();
                    for(const measurement of measurements) {
                        $("#measurementDropDown"+i).append($("<option></option>").attr("value", measurement).text(measurement));
                        console.log(measurement);
                    }
                }
            }
        });
    }

    $.ajax({
        url: "/api/getAllIngredients",
        method: "GET",
        dataType: "json",
        success: function (data) {
            ingredients = data;
            console.log(ingredients);
            addIngredientDropdown();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $("#addIngredient").on("click", addIngredientDropdown);

    let numEquipment = 0;
    let equipment = {};

    function addEquipmentDropdown() {
        numEquipment++;
        let dropdown = "<select id='equipmentDropDown"+numEquipment+"' class='selectpicker' data-live-search='true'>";
        dropdown += "<option value=''></option>";
        for(const e of equipment) {
            dropdown += "<option value='"+e.equipment+"'>"+e.equipment+"</option>";
        }
        dropdown += "</select>";
        $("#equipmentList").append(dropdown);
    }

    $.ajax({
        url: "/api/getAllEquipment",
        method: "GET",
        dataType: "json",
        success: function (data) {
            equipment = data;
            console.log(equipment);
            addEquipmentDropdown();
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $("#addEquipment").on("click", addEquipmentDropdown);

    $("#imageURL").on("change", function(){
       let url = $("#imageURL").val();
       $("#imagePreview").attr("src", url);
    });

    $("#submit").on("click", function(){
       var recipeName = $("#recipeName").val();
       var imageURL = $("#imageURL").val();
       var instructions = $("#instructions").val();
       var ingredientVals = [];
       var equipmentVals = [];

       for(var i = 1; i <= numIngredients; i++) {
            let ingredient = {};
            ingredient["ingredientID"] = $("#ingredientDropDown"+i).val();
            ingredient["amount"] = $("#amount"+i).val();
            ingredient["measurement"] = $("#measurementDropDown"+i).val();
            ingredientVals.push(ingredient);
       }
       for(var i = 1; i <= numEquipment; i++) {
            equipmentVals.push($("#equipmentDropDown"+i).val());
       }

       let recipe = {};
       recipe["userID"] = userID;
       recipe["recipeName"] = recipeName;
       recipe["imageURL"] = imageURL;
       recipe["instructions"] = instructions;
       recipe["ingredients"] = ingredientVals;
       recipe["equipment"] = equipmentVals;
       console.log(recipe);

       $.ajax({
            url: "/api/createRecipe",
            method: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(recipe),
            success: function (data) {
                console.log(data);
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });

});