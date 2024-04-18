function toggle_index() {
    // Find elements
    var list = document.getElementById("list");
    var map = document.getElementById("map");
    var button = document.getElementById("toggle_button");

    // Toggle between displays
    if (map.style.display == "block") {
        map.style.display = "none";
        list.style.display = "block";
        button.innerHTML = "Show map view";
    }
    else {
        list.style.display = "none";
        map.style.display = "block";
        button.innerHTML = "Show list view";
    }
}