function toggle(divID) {
    // Find div to show or hide
    var element = document.getElementById(divID);

    // Find corresponding button
    var buttonID = divID + "_button";
    var button = document.getElementById(buttonID);

    // Toggle visibility and button text
    if (element.style.display == "block") {
        element.style.display = "none";
        button.innerHTML = "Show";
    } 
    else {
        element.style.display = "block";
        button.innerHTML = "Hide";
    }
}