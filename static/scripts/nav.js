$(document).ready(function() {


    const userID = sessionStorage.getItem('userID');
    if(userID != null) {
        $(".rightnav").empty().append("<a class='navItem' href='/profile'>Profile</a><a class='navItem' href='#' id='signout'>Sign Out</a>")
        $("#signout").on("click", function() {
            sessionStorage.removeItem("userID");
            sessionStorage.removeItem("username");
            window.location.href = "/";
        });
    }


});