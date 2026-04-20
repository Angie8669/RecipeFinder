const userID = sessionStorage.getItem('userID');
if(userID == null) {
    window.location.replace("/login");
}

$(document).ready(function() {
    let numIngredients = 0;
    let ingredients = {};

    function addIngredientDropdown() {
        numIngredients++;
        let dropdown = "<select id='ingredientDropDown"+numIngredients+"' class='selectpicker' data-live-search='true'>";
        dropdown += "<option value=''></option>";
        for(const ingredient of ingredients) {
            dropdown += "<option value='"+ingredient.ingredientID+"'>"+ingredient.ingredientName+"</option>";
        }
        dropdown += "</select>";
        $("#ingredientList").append(dropdown);
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
       var imageURL = $("#ImageURL").val();
       var instructions = $("#instructions").val();
       var ingredientVals = [];
       var equipmentVals = [];
       for(var i = 1; i <= numIngredients; i++) {
            ingredientVals.push($("#ingredientDropDown"+i).val());
       }
       for(var i = 1; i <= numEquipment; i++) {
            equipmentVals.push($("#equipmentDropDown"+i).val());
       }
    });

});