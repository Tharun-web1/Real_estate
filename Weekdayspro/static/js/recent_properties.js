// recent_properties.js

function toggleFilters() {
    const box = document.getElementById("filterBox");
    if (box) {
        box.classList.toggle("open");
    }
}

function applyQuickFilter(type) {
    const url = new URL(window.location.href);
    url.searchParams.set("look", type);
    window.location.href = url.toString();
}

function shareProject(title, address, price, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: `${title} at ${address} for ₹${price}`,
            url: window.location.origin + url
        });
    } else {
        navigator.clipboard.writeText(window.location.origin + url);
        alert("Link copied to clipboard!");
    }
}

function toggleSave(event, id, btn) {
    event.stopPropagation();
    fetch(`/save/${id}/`)
        .then(res => res.json())
        .then(data => {
            const icon = btn.querySelector("i");
            if (data.status === "saved") {
                icon.classList.remove("bi-bookmark");
                icon.classList.add("bi-bookmark-fill");
            } else {
                icon.classList.remove("bi-bookmark-fill");
                icon.classList.add("bi-bookmark");
            }
        });
}

function redirectToLogin() {
    window.location.href = "/login/";
}

// Google Maps Autocomplete
let autocompleteInitialized = false;
function initAutocomplete() {
    if (autocompleteInitialized) return;
    const input = document.getElementById("locationSearch");
    if (!input || !window.google) return;

    const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ["(cities)"],
        componentRestrictions: { country: "in" },
    });

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (place.address_components) {
            let city = "";
            place.address_components.forEach(c => {
                if (c.types.includes("locality")) city = c.long_name;
            });
            if (city) input.value = city;
        }
    });
    autocompleteInitialized = true;
}

function onGoogleMapsLoaded() {
    initAutocomplete();
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.google) initAutocomplete();
});
