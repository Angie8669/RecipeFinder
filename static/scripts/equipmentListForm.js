const userID = sessionStorage.getItem('userID');
if(userID == null) {
    window.location.replace("/login");
}

$(document).ready(function() {
    let numEquipment = 0;
    let equipment = {};

    function addEquipmentDropdown() {
        numEquipment++;

        let equipmentHTML = "<select id='equipmentDropDown"+numEquipment+"'>";
        equipmentHTML += "<option value=''></option>";
        for(const equipmentVal of equipment) {
            equipmentHTML += "<option value='"+equipmentVal.equipment+"'>"+equipmentVal.equipment+"</option>";
        }
        equipmentHTML += "</select>";
        $("#equipmentList").append(equipmentHTML);
    }

    $.ajax({
        url: "/api/getAllEquipment",
        method: "GET",
        dataType: "json",
        success: function (data) {
            equipment = data;
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
            numEquipment = data.length;
            for(let i = 1; i <= numEquipment; i++) {
                const val = data[i-1];

                let equipmentHTML = "<select id='equipmentDropDown"+i+"'>";
                equipmentHTML += "<option value=''></option>";

                for(const equipmentVal of equipment) {
                    if(equipmentVal.equipment == val.equipment) {
                        equipmentHTML += "<option value='"+equipmentVal.equipment+"' selected>"+equipmentVal.equipment+"</option>";
                    } else {
                        equipmentHTML += "<option value='"+equipmentVal.equipment+"'>"+equipmentVal.equipment+"</option>";
                    }
                }
                equipmentHTML += "</select>";
                $("#equipmentList").append(equipmentHTML);
            }
        },
        error: function (xhr, status, err) {
            console.error("Error:", status, err);
            $("#errorMessage").text(xhr.responseText);
            return false;
        }
    });

    $("#addEquipment").on("click", addEquipmentDropdown);


    $("#submit").on("click", function(){
       var equipmentVals = [];

       for(var i = 1; i <= numEquipment; i++) {
            let equipmentData = [];
            equipmentVals.push($("#equipmentDropDown"+i).val());
       }

       let equipmentList = {};

       equipmentList["userID"] = userID;
       equipmentList["equipment"] = equipmentVals;
       console.log(equipmentList);

       $.ajax({
            url: "/api/updateEquipmentList",
            method: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(equipmentList),
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