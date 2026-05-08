function initAutocomplete() {
  const input = document.getElementById("citySearch");

  const options = {
    types: ["(cities)"], // ONLY cities
    componentRestrictions: { country: "in" }, // only INDIA (remove if not needed)
  };

  const autocomplete = new google.maps.places.Autocomplete(input, options);

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    console.log(place);
  });
}

google.maps.event.addDomListener(window, "load", initAutocomplete);
