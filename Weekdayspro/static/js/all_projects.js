/* all_projects.js */

function toggleFilters() {
    const box = document.querySelector(".filter-box");
    const btn = document.querySelector(".filter-toggle-btn");
    box.classList.toggle("open");
    if (box.classList.contains("open")) {
        btn.innerHTML = '<i class="bi bi-x-lg"></i> Close Filters';
    } else {
        btn.innerHTML = '<i class="bi bi-filter"></i> Filters';
    }
}

function toggleProjectSave(event, id, btn) {
    event.preventDefault();
    fetch(`/save-project/${id}/`)
        .then(res => res.json())
        .then(data => {
            let icon = btn.querySelector("i");
            if (data.status === "saved") {
                icon.classList.remove("bi-bookmark");
                icon.classList.add("bi-bookmark-fill");
                btn.classList.add('active');
            } else {
                icon.classList.remove("bi-bookmark-fill");
                icon.classList.add("bi-bookmark");
                btn.classList.remove('active');
            }
        })
        .catch(err => console.error('Error saving project:', err));
}

function redirectToLogin() {
    window.location.href = loginUrl; // loginUrl should be defined in the template
}

function onGoogleMapsLoaded() {
    const input = document.getElementById("location-input");
    if (!input) return;
    const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ["(cities)"],
        componentRestrictions: { country: "in" }
    });
}

function shareProject(name, location, price, url) {
    const fullUrl = window.location.origin + url;
    const message = 
        "🏗 Project: " + name + "\n" +
        "📍 Location: " + location + "\n" +
        "💰 Price: ₹" + price + "\n\n" +
        "View Project 👇";

    if (navigator.share) {
        navigator.share({
            title: name,
            text: message,
            url: fullUrl
        }).catch(err => console.log(err));
    } else {
        navigator.clipboard.writeText(message + "\n" + fullUrl)
            .then(() => alert("Project link copied to clipboard"))
            .catch(err => console.error('Error copying to clipboard:', err));
    }
}


// Pull to refresh logic is already handled in NavBar.html

