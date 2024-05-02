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
    });

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        minZoom: 6,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add a marker for each park
    var greenIcon = new L.Icon({
        iconUrl: '{{ url_for('static', filename='img/marker-icon-green.png') }}',
        shadowUrl: '{{ url_for('static', filename='img/marker-shadow.png') }}',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    var yellowIcon = new L.Icon({
        iconUrl: '{{ url_for('static', filename='img/marker-icon-gold.png') }}',
        shadowUrl: '{{ url_for('static', filename='img/marker-shadow.png') }}',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    var redIcon = new L.Icon({
        iconUrl: '{{ url_for('static', filename='img/marker-icon-red.png') }}',
        shadowUrl: '{{ url_for('static', filename='img/marker-shadow.png') }}',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    {% for p in parks %}
    L.marker([{{ p['latitude'] }}, {{ p['longitude'] }}], {icon: 
        {% if p['level'] == 'bad' %}
        redIcon
        {% elif p['level'] == 'warning' %}
        yellowIcon
        {% else %}
        greenIcon
        {% endif %}
    }).addTo(map)
    .bindPopup('<a href="{{ url_for('park', park_id=p['park_id']) }}" target="_blank">{{ p['name'] }}</a>')
    .on('click', (e) => {e.target.openPopup()});
    {% endfor %}
};

addEventListener("load", addMap);