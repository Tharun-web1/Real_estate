/* ── Share Profile ──────────────────────────────────── */
function shareProfile(id) {
  if (navigator.share) {
    navigator.share({
      title: "User Profile",
      text: "Check out this profile",
      url: window.location.origin + "/user/" + id,
    });
  } else {
    navigator.clipboard.writeText(
      window.location.origin + "/user/" + id
    );
    alert("Profile link copied!");
  }
}

/* ── Google Maps Autocomplete ───────────────────────── */
let autocompleteInitialized = false;

function initAutocomplete() {
  if (autocompleteInitialized) return;

  const input = document.getElementById("locationSearch");
  if (!input) return;

  if (!window.google || !google.maps || !google.maps.places) {
    console.warn("Google Maps not loaded yet");
    return;
  }

  const autocomplete = new google.maps.places.Autocomplete(input, {
    types: ["(cities)"],
    componentRestrictions: { country: "in" },
  });

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    if (!place.address_components) return;

    let city = "";
    place.address_components.forEach((component) => {
      if (component.types.includes("locality")) {
        city = component.long_name;
      }
      if (!city && component.types.includes("administrative_area_level_2")) {
        city = component.long_name;
      }
    });

    input.value = city;
  });

  autocompleteInitialized = true;
}

/* Called by Google Maps async callback */
window.onGoogleMapsLoaded = function () {
  initAutocomplete();
};
