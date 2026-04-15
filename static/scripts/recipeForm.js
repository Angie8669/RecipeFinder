$(document).ready(function() {
    $("#ImageURL").on("change", function(){
       console.log("Test");
       let url = $("#ImageURL").val();
       $("#ImagePreview").attr("src", url);
    });
});