function search() {
    var input = $("[name='search']").val();
    console.log("Search: " + input);

    $.ajax({
        url: `/search/${encodeURIComponent(input)}`,
        method: "GET",
        dataType: "json",
        success: function (data) {
            $("#result_list").empty();
            for(var i = 0; i < data.length; i++) {
                $("#result_list").append(
                    "<div class='song'>"
                    + data[i].name + ": " + data[i].artist + " " + data[i].genre
                    + "<img src='" + data[i].image + "'></img>"
                    + "</div");
            }
            console.log(data);
        },
        error: function (xhr, status, err) {
        console.error("Error:", status, err, xhr.responseText);
        }
    });
}