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
                if(ingredient.ingredientID == curVal && ingredient.possibleMeasurements != null) {
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
            numIngredients = data.length;
            for(let i = 1; i <= numIngredients; i++) {
                const val = data[i-1];

                let ingredientHTML = "<input type='number' value='"+val.amount+"' step='0.0625' id='amount"+i+"'/>"

                ingredientHTML += "<select id='measurementDropDown"+i+"'>";
                for(const ingredient of ingredients) {
                    if(ingredient.ingredientID == val.ingredientID && ingredient.possibleMeasurements != null) {
                        const measurements = ingredient.possibleMeasurements.split(",");
                        for(const measurement of measurements) {
                            if(measurement == val.measurement) {
                                ingredientHTML += "<option value='"+measurement+"' selected>"+measurement+"</option>";
                            } else {
                                ingredientHTML += "<option value='"+measurement+"'>"+measurement+"</option>";
                            }
                        }
                    }
                }
                ingredientHTML += "</select>";

                ingredientHTML += "<select id='ingredientDropDown"+i+"'>";
                ingredientHTML += "<option value=''></option>";

                for(const ingredient of ingredients) {
                    if(ingredient.ingredientID == val.ingredientID) {
                        ingredientHTML += "<option value='"+ingredient.ingredientID+"' selected>"+ingredient.ingredientName+"</option>";
                    } else {
                        ingredientHTML += "<option value='"+ingredient.ingredientID+"'>"+ingredient.ingredientName+"</option>";
                    }
                }
                ingredientHTML += "</select>";
                $("#ingredientList").append(ingredientHTML);

                $("#ingredientDropDown"+i).on("change", function(event){

                    let j = event.target.id.replace("ingredientDropDown", "");

                    let curVal = $("#ingredientDropDown"+j).val();
                    for(const ingredient of ingredients) {
                        if(ingredient.ingredientID == curVal && ingredient.possibleMeasurements != null) {
                            const measurements = ingredient.possibleMeasurements.split(",");
                            console.log(measurements);
                            $("#measurementDropDown"+j).empty();
                            for(const measurement of measurements) {
                                $("#measurementDropDown"+j).append($("<option></option>").attr("value", measurement).text(measurement));
                                console.log(measurement);
                            }
                        }
                    }
                });
            }
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $("#addIngredient").on("click", addIngredientDropdown);


    $("#submit").on("click", function(){

       var ingredientVals = [];


       for(var i = 1; i <= numIngredients; i++) {
            let ingredient = {};
            ingredient["ingredientID"] = $("#ingredientDropDown"+i).val();
            ingredient["amount"] = $("#amount"+i).val();
            ingredient["measurement"] = $("#measurementDropDown"+i).val();
            ingredientVals.push(ingredient);
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
                //window.location.href="/profile";
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });


});