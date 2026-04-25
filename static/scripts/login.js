$(document).ready(function() {
    $("#loginForm").submit(function(e) {
        e.preventDefault();
        e.stopPropagation();

        var username = $("[name='username']").val();
        var password = $("[name='password']").val();

        if (username === '') {
            $("#errorMessage").text("Username is empty.");
            return false;
        }
        if (password === '') {
            $("#errorMessage").text("Password is empty.");
            return false;
        }

        $.ajax({
            url: "/authenticate?username="+username + "&password="+password,
            method: "GET",
            dataType: "json",
            success: function (data) {
                console.log(data);
                sessionStorage.setItem("userID", data.userID);
                sessionStorage.setItem("username", data.username);
                window.location.href = "/";
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });
});