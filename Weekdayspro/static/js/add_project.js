/* add_project.js */
console.log("add_project.js loading...");

// Fallback for CSS.escape if it doesn't exist
if (!window.CSS || !window.CSS.escape) {
  window.CSS = window.CSS || {};
  window.CSS.escape = function(v) {
    return v.replace(/([^\w\-])/g, "\\$1");
  };
}

document.addEventListener("DOMContentLoaded", function () {
  // Image preview
  const imageInput = document.getElementById("imageInput");
  if (imageInput) {
    imageInput.addEventListener("change", function () {
      const preview = document.getElementById("imagePreview");
      preview.innerHTML = "";

      if (this.files.length > 10) {
        alert("You can upload maximum 10 images");
        this.value = "";
        return;
      }

      Array.from(this.files).forEach(file => {
        const reader = new FileReader();
        reader.onload = function (e) {
          let img = document.createElement("img");
          img.src = e.target.result;
          preview.appendChild(img);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // Initialize nearby remove buttons
  updateRemoveButtons();

  // Position select change
  const positionSelect = document.getElementById("positionSelect");
  if (positionSelect) {
    positionSelect.addEventListener("change", function () {
      let value = this.value;
      let box = document.getElementById("constructionTimeBox");
      let input = document.getElementById("constructionTimeInput");

      if (value === "UNDER") {
        box.style.display = "block";
        input.required = true;
      } else {
        box.style.display = "none";
        input.required = false;
        input.value = ""; // clear if not needed
      }
    });
  }
});

// Add new nearby field
function addNearbyField() {
  const container = document.getElementById("nearby-container");
  const div = document.createElement("div");
  div.classList.add("nearby-item");
  div.innerHTML = `
    <input type="text" name="nearby_locations[]" placeholder="e.g. Hospital (2 km)" required>
    <button type="button" class="remove-nearby-btn" onclick="removeField(this)">✕</button>
  `;
  container.appendChild(div);
  updateRemoveButtons();
}

// Remove field
function removeField(btn) {
  const container = document.getElementById("nearby-container");
  const item = btn.parentElement;
  if (container.children.length > 1) {
    item.remove();
  } else {
    alert("At least one nearby place is required");
  }
  updateRemoveButtons();
}

// Hide remove button for first field
function updateRemoveButtons() {
  const items = document.querySelectorAll(".nearby-item");
  items.forEach((item, index) => {
    const btn = item.querySelector(".remove-nearby-btn");
    if (btn) {
      if (index === 0) {
        btn.style.display = "none"; // hide first
      } else {
        btn.style.display = "block";
      }
    }
  });
}

// Validate nearby fields
function validateNearby() {
  const inputs = document.querySelectorAll("#nearby-container input[name='nearby_locations[]']");
  let valid = false;
  inputs.forEach(input => {
    if (input.value.trim() !== "") {
      valid = true;
    }
  });
  if (!valid) {
    alert("Please add at least one nearby place");
    return false;
  }
  return true;
}

// Generic Media Preview
function previewGenericMedia(input, previewId) {
  const previewContainer = document.getElementById(previewId);
  previewContainer.innerHTML = "";
  if (input.files && input.files.length > 0) {
    Array.from(input.files).forEach(file => {
      const fileType = file.type;
      if (fileType.startsWith('video/')) {
        const video = document.createElement("video");
        video.src = URL.createObjectURL(file);
        video.style.width = "100px";
        video.style.height = "100px";
        video.style.objectFit = "cover";
        video.style.borderRadius = "8px";
        video.style.border = "1px solid #ddd";
        video.controls = false;
        previewContainer.appendChild(video);
      } else {
        const fileName = document.createElement("div");
        fileName.className = "file-name";
        fileName.style.fontSize = "13px";
        fileName.style.color = "#6b7280";
        fileName.style.background = "#e5e7eb";
        fileName.style.padding = "4px 8px";
        fileName.style.borderRadius = "4px";
        fileName.style.display = "inline-block";
        fileName.innerHTML = `<i class="bi bi-file-earmark"></i> ` + file.name;
        previewContainer.appendChild(fileName);
      }
    });
  }
}

// Legal Documents Functions
function previewLegalDoc(input) {
  const previewContainer = input.closest('.legal-doc-item').querySelector('.doc-preview');
  previewContainer.innerHTML = "";
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const fileType = file.type;
    if (fileType.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result;
        previewContainer.appendChild(img);
      }
      reader.readAsDataURL(file);
    } else {
      const fileName = document.createElement("div");
      fileName.className = "file-name";
      fileName.innerHTML = `<i class="bi bi-file-earmark-pdf"></i> ` + file.name;
      previewContainer.appendChild(fileName);
    }
  }
}

function addLegalDoc() {
  const container = document.getElementById("legal-docs-container");
  const div = document.createElement("div");
  div.classList.add("legal-doc-item");
  div.innerHTML = `
    <div class="legal-doc-row" style="align-items: center; flex-wrap: wrap;">
      <input type="text" name="legal_doc_name[]" placeholder="Document Name" class="doc-name-input" required style="max-width: 220px;">
      <label class="upload-plus-btn" title="Upload Document" style="flex-shrink: 0;">
        <i class="bi bi-plus-lg"></i>
        <input type="file" name="legal_doc_file[]" class="doc-file-input" accept="image/*,application/pdf" onchange="previewLegalDoc(this)" required>
      </label>
      <div class="doc-preview" style="flex: 1; margin-top: 0; display: flex; gap: 10px;"></div>
      <button type="button" class="remove-doc-btn" onclick="removeLegalDoc(this)" style="flex-shrink: 0;"><i class="bi bi-trash"></i></button>
    </div>
  `;
  container.appendChild(div);
}

function removeLegalDoc(btn) {
  const container = document.getElementById("legal-docs-container");
  const item = btn.closest(".legal-doc-item");
  if (container.children.length > 1) {
    item.remove();
  }
}

// Step Navigation
function goToStep(stepNumber, requiredFields) {
  function findField(identifier) {
    if (!identifier) return null;
    let el = document.getElementById(identifier);
    if (el) return el;
    el = document.querySelector('[name="' + CSS.escape(identifier) + '"]');
    return el;
  }

  function clearValidation(stepEl) {
    (stepEl.querySelectorAll("input,textarea,select") || []).forEach(f => {
      f.style.border = "";
    });
  }

  const currentStepEl = document.querySelector(".step.active") || document.getElementById("step" + stepNumber);
  if (!currentStepEl) return;

  let toValidate = [];
  if (Array.isArray(requiredFields) && requiredFields.length > 0) {
    requiredFields.forEach(idOrName => {
      const fld = findField(idOrName);
      if (fld) toValidate.push(fld);
    });
  }

  if (toValidate.length === 0) {
    const requiredEls = currentStepEl.querySelectorAll("input[required], textarea[required], select[required]");
    requiredEls.forEach(e => toValidate.push(e));
  }

  let valid = true;
  let firstInvalid = null;
  clearValidation(currentStepEl);

  toValidate.forEach(field => {
    if (field.disabled || field.type === "hidden") return;
    let empty = false;
    if (field.type === "checkbox" || field.type === "radio") {
      const name = field.name;
      if (name) {
        const group = document.querySelectorAll('[name="' + CSS.escape(name) + '"]');
        let anyChecked = false;
        group.forEach(g => { if (g.checked) anyChecked = true; });
        if (!anyChecked) empty = true;
      } else {
        if (!field.checked) empty = true;
      }
    } else {
      const val = (field.value || "").trim();
      if (val === "") empty = true;
    }
    if (empty) {
      valid = false;
      field.style.border = "2px solid #e74c3c";
      if (!firstInvalid) firstInvalid = field;
    }
  });

  if (!valid) {
    if (firstInvalid && typeof firstInvalid.focus === "function") firstInvalid.focus();
    return;
  }

  document.querySelectorAll(".step").forEach(s => s.classList.remove("active"));
  const target = document.getElementById("step" + stepNumber);
  if (target) {
    target.classList.add("active");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// Maps and Marker
let map;
let marker;
let autocomplete;
let geocoder;

function initMap() {
  const defaultLocation = { lat: 17.385044, lng: 78.486671 };
  const mapElement = document.getElementById("map");
  if (!mapElement) return;

  map = new google.maps.Map(mapElement, {
    center: defaultLocation,
    zoom: 13
  });
  geocoder = new google.maps.Geocoder();
  marker = new google.maps.Marker({
    position: defaultLocation,
    map: map,
    draggable: true
  });
  const searchInput = document.getElementById("search_location");
  if (searchInput) {
    autocomplete = new google.maps.places.Autocomplete(searchInput);
    autocomplete.bindTo("bounds", map);
    autocomplete.addListener("place_changed", function () {
      const place = autocomplete.getPlace();
      if (!place.geometry) return;
      const location = place.geometry.location;
      map.setCenter(location);
      map.setZoom(15);
      marker.setPosition(location);
      updateFields(location.lat(), location.lng(), place.formatted_address);
    });
  }

  google.maps.event.addListener(marker, "dragend", function () {
    const position = marker.getPosition();
    geocoder.geocode({ location: position }, function (results, status) {
      if (status === "OK" && results[0]) {
        if (searchInput) searchInput.value = results[0].formatted_address;
        updateFields(position.lat(), position.lng(), results[0].formatted_address);
      }
    });
  });

  updateFields(defaultLocation.lat, defaultLocation.lng);
}

function updateFields(lat, lng, address = "") {
  const latField = document.getElementById("id_latitude");
  const lngField = document.getElementById("id_longitude");
  const urlField = document.getElementById("id_location_url");
  if (latField) latField.value = lat;
  if (lngField) lngField.value = lng;
  if (address) {
    const locationInput = document.querySelector("input[name='project_address']");
    if (locationInput) locationInput.value = address;
  }
  const mapUrl = `https://www.google.com/maps?q=${lat},${lng}`;
  if (urlField) urlField.value = mapUrl;
}

function validateFinalStep() {
  const imageInput = document.getElementById("imageInput");
  const videoInput = document.getElementById("videoInput");
  let valid = true;
  if (imageInput && imageInput.files.length === 0) {
    alert("Please upload at least one image.");
    imageInput.style.border = "2px solid red";
    valid = false;
  }
  if (videoInput && videoInput.files.length === 0) {
    alert("Please upload at least one video.");
    videoInput.style.border = "2px solid red";
    valid = false;
  }
  return valid;
}

window.goToStep = goToStep;
window.addNearbyField = addNearbyField;
window.removeField = removeField;
window.addLegalDoc = addLegalDoc;
window.removeLegalDoc = removeLegalDoc;
window.previewGenericMedia = previewGenericMedia;
window.previewLegalDoc = previewLegalDoc;
window.initMap = initMap;

// Robust map initialization
if (typeof google !== 'undefined') {
    initMap();
} else {
    window.addEventListener('load', function() {
        if (typeof google !== 'undefined') initMap();
    });
}
