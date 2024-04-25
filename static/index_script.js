function toggle_index() {
    // Find elements to toggle
    var list = document.getElementById("list");
    var map = document.getElementById("map");
    var button = document.getElementById("toggle_button");

    // Toggle between displays
    if (list.style.display == "block") {
        list.style.display = "none";
        map.style.display = "block";
        button.innerHTML = "Show list view";
    }
    else {
        map.style.display = "none";
        list.style.display = "block";
        button.innerHTML = "Show map view";
    }
};

function addMap() {
    // Add map
    var map = L.map("map", {
        center: [46.5, -94.6],
        zoom: 6
    })

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        minZoom: 6,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add a marker for each park
    L.marker([44.84681, -92.79139]).addTo(map)
    .bindPopup('<a href="">Afton State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([46.17349, -92.84968]).addTo(map)
    .bindPopup('<a href="">Banning State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.52373, -92.34214]).addTo(map)
    .bindPopup('<a href="">Frontenac State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([47.14092, -91.46971]).addTo(map)
    .bindPopup('<a href="">Gooseberry Falls State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([48.00055, -89.59312]).addTo(map)
    .bindPopup('<a href="">Grand Portage State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([43.93956, -91.40834]).addTo(map)
    .bindPopup('<a href="">Great River Bluffs State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([45.39366, -92.66899]).addTo(map)
    .bindPopup('<a href="">Interstate State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([46.65433, -92.37127]).addTo(map)
    .bindPopup('<a href="">Jay Cooke State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([45.31376, -93.94101]).addTo(map)
    .bindPopup('<a href="">Lake Maria State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([46.13559, -93.72518]).addTo(map)
    .bindPopup('<a href="">Mille Lacs Kathio State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([43.63729, -93.30918]).addTo(map)
    .bindPopup('<a href="">Myre-Big Island State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.34225, -93.10519]).addTo(map)
    .bindPopup('<a href="">Nerstrand Big Woods State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([45.94622, -92.60659]).addTo(map)
    .bindPopup('<a href="">St. Croix State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([47.33848, -91.19606]).addTo(map)
    .bindPopup('<a href="">Tettegouche State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.06227, -92.04486]).addTo(map)
    .bindPopup('<a href="">Whitewater State Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([45.22504, -92.76562]).addTo(map)
    .bindPopup("<a href=''>William O'Brien State Park</a>")
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.78643, -93.12888]).addTo(map)
    .bindPopup('<a href="">Lebanon Hills Regional Park</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.76568, -92.93711]).addTo(map)
    .bindPopup('<a href="">Spring Lake Park Reserve</a>')
    .on('click', (e) => {e.target.openPopup()});

    L.marker([44.72505, -92.84999]).addTo(map)
    .bindPopup('<a href="">Vermillion Falls Park</a>')
    .on('click', (e) => {e.target.openPopup()});
};

addEventListener("load", addMap);