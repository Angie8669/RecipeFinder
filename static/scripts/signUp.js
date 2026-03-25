
$(document).ready(function() {
    $("#signUpForm").submit(function(e) {
        e.preventDefault();
        e.stopPropagation();

        var firstName = $("[name='firstName']").val();
        var lastName = $("[name='lastName']").val();
        var username = $("[name='username']").val();
        var password = $("[name='password']").val();
        var password2 = $("[name='password2']").val();

        console.log(firstName);
        if (firstName === '') {
            $("#errorMessage").text("First name is empty.");
            return false;
        }
        if (lastName === '') {
            $("#errorMessage").text("Last name is empty.");
            return false;
        }
        if (username === '') {
            $("#errorMessage").text("Username is empty.");
            return false;
        }
        if (password === '') {
            $("#errorMessage").text("Password is empty.");
            return false;
        }
        if (password2 != password) {
            $("#errorMessage").text("Passwords do not match.");
            return false;
        }

        var params = {
            "firstName": firstName,
            "lastName": lastName,
            "username": username,
            "password": password
        }
        $.ajax({
            url: "/createUser",
            method: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(params),
            success: function (data) {
                console.log(data);
                window.location.href = "/login";
            },
            error: function (xhr, status, err) {
                console.error("Error:", status, err);
                $("#errorMessage").text(xhr.responseText);
                return false;
            }
        });
    });
});