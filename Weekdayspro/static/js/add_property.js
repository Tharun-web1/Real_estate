/* ==========================================================
   HELPER FUNCTIONS
========================================================== */
function setupDragAndDrop(zoneId, inputId, callback) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);

    if (!zone || !input) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        zone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        zone.addEventListener(eventName, () => zone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        zone.addEventListener(eventName, () => zone.classList.remove('drag-over'), false);
    });

    zone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (zoneId === 'imageDropZone') {
            distributeFiles(dt.files);
        } else {
            input.files = dt.files;
            input.dispatchEvent(new Event('change'));
        }
    }, false);
}

function distributeFiles(files) {
    const previewRow = document.getElementById('imagePreviewRow');
    const realInputs = [
        document.getElementById('id_image'),
        document.getElementById('id_image1'),
        document.getElementById('id_image2'),
        document.getElementById('id_image3'),
        document.getElementById('id_image4')
    ];
    
    const fileArray = Array.from(files).slice(0, 5);
    previewRow.innerHTML = ''; // Reset previews

    fileArray.forEach((file, i) => {
        if (i < realInputs.length) {
            const dt = new DataTransfer();
            dt.items.add(file);
            realInputs[i].files = dt.files;
            createHorizontalPreview(file, i);
        }
    });
}

function createHorizontalPreview(file, index) {
    const previewRow = document.getElementById('imagePreviewRow');
    const realInputs = [
        document.getElementById('id_image'),
        document.getElementById('id_image1'),
        document.getElementById('id_image2'),
        document.getElementById('id_image3'),
        document.getElementById('id_image4')
    ];

    const reader = new FileReader();
    reader.onload = e => {
        const card = document.createElement('div');
        card.className = 'prop-preview-card';
        
        const img = document.createElement('img');
        img.src = e.target.result;
        
        const removeBtn = document.createElement('div');
        removeBtn.className = 'prop-remove-tag';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => {
            realInputs[index].value = '';
            card.remove();
        };
        
        card.appendChild(img);
        card.appendChild(removeBtn);
        previewRow.appendChild(card);
    };
    reader.readAsDataURL(file);
}

function clearMediaInput(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (input) {
        input.value = '';
        input.dispatchEvent(new Event('change'));
    }
    if (preview) preview.innerHTML = '';
}

/* ==========================================================
   NEARBY PLACES LOGIC
========================================================== */
window.syncNearbyData = function() {
    const container = document.getElementById("nearby-container");
    const hiddenField = document.getElementById("nearby_places_text");
    if (!container || !hiddenField) return;

    const inputs = container.querySelectorAll(".nearby-input");
    const nearbyPlaces = [];

    inputs.forEach(inp => {
        const val = inp.value.trim();
        if (val) nearbyPlaces.push(val);
    });

    hiddenField.value = JSON.stringify(nearbyPlaces);
}

window.addNearbyField = function () {
    const container = document.getElementById("nearby-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "nearby-item";
    div.innerHTML = `
        <input type="text" class="nearby-input" placeholder="e.g. School (1 km)">
        <span class="remove-x" onclick="removeNearbyField(this)">×</span>
    `;
    container.appendChild(div);
};

window.removeNearbyField = function (el) {
    if (el && el.parentElement) {
        el.parentElement.remove();
        syncNearbyData();
    }
};


/* ==========================================================
   MULTI-STEP FORM LOGIC
========================================================== */
let currentStep = 1;
const formSteps = document.querySelectorAll(".form-step");

function showStep(stepNumber) {
    const steps = document.querySelectorAll(".form-step");
    steps.forEach((step, index) => {
        step.classList.toggle("active", index + 1 === stepNumber);
    });
}

function nextStep() {
    if (currentStep === 1) {
        const lookValue = document.querySelector('input[name="look"]').value;
        const propValue = document.querySelector('input[name="selectProperty"]').value;

        // Clear old errors
        document.getElementById("lookError").innerText = "";
        document.getElementById("propertyError").innerText = "";

        let hasError = false;
        if (!lookValue) {
            document.getElementById("lookError").innerText = "Please select what you are looking to do.";
            hasError = true;
        }
        if (!propValue) {
            document.getElementById("propertyError").innerText = "Please select a property type.";
            hasError = true;
        }
        if (hasError) return;
    }

    if (currentStep === 2) {
        const activeFieldSet = document.querySelector("#step-2 .conditional-fields.active-fieldset");
        if (activeFieldSet) {
            const requiredFields = activeFieldSet.querySelectorAll("[data-required='true']:not(:disabled)");
            if (!validateFields([...requiredFields])) return;
        }
    }

    if (currentStep === 3) {
        // Sync nearby places before validation
        if (typeof syncNearbyData === "function") syncNearbyData();

        let hasStep3Error = false;

        const showFieldError = (container, message) => {
            hasStep3Error = true;
            const oldError = container.querySelector(".error-message");
            if (oldError) oldError.remove();

            const error = document.createElement("span");
            error.className = "error-message";
            error.style.cssText = "color:#e53e3e; font-size:12px; display:block; margin-top:4px; font-weight:600;";
            error.innerText = `⚠ ${message}`;
            container.appendChild(error);
            container.style.border = "1px solid #e53e3e";
            container.style.padding = "5px";
            container.style.borderRadius = "8px";
        };

        const clearFieldError = (container) => {
            const oldError = container.querySelector(".error-message");
            if (oldError) oldError.remove();
            container.style.border = "";
            container.style.padding = "";
        };

        const reraSection = document.getElementById("reraSection");
        if (reraSection && reraSection.style.display !== "none") {
            const reraInputs = document.getElementsByName("reraApproved");
            let reraSelected = false;
            reraInputs.forEach(input => { if (input.checked) reraSelected = true; });
            clearFieldError(reraSection);
            if (!reraSelected) showFieldError(reraSection, "Please select if the property is RERA Approved.");
        }

        const amenitiesSection = document.getElementById("amenitiesSection");
        if (amenitiesSection && amenitiesSection.style.display !== "none") {
            const amenityInputs = document.querySelectorAll('input[name="predefined_amenities"]');
            let amenitySelected = false;
            amenityInputs.forEach(input => { if (input.checked) amenitySelected = true; });

            const addedAmenitiesList = document.getElementById("addedAmenitiesList");
            const hasCustomAmenities = addedAmenitiesList && addedAmenitiesList.children.length > 0;

            clearFieldError(amenitiesSection);
            if (!amenitySelected && !hasCustomAmenities) {
                showFieldError(amenitiesSection, "Please select at least one predefined amenity or add a custom one.");
            }
        }

        const mapContainer = document.getElementById("map").parentElement;
        const latitude = document.getElementById("id_latitude");
        const locationField = document.getElementById("id_location");
        clearFieldError(mapContainer);
        if (!latitude.value || !locationField.value) {
            showFieldError(mapContainer, "Please search for a location or drag the map marker to a specific address.");
        }

        const nearbyBox = document.querySelector(".nearby-box");
        const nearbyField = document.getElementById("nearby_places_text");
        clearFieldError(nearbyBox);
        if (nearbyField) {
            let nearbyPlaces = [];
            try { nearbyPlaces = JSON.parse(nearbyField.value || "[]"); } catch(e) { nearbyPlaces = []; }
            if (nearbyPlaces.length === 0) showFieldError(nearbyBox, "Please add at least one nearby place.");
        }

        if (hasStep3Error) return;

        const fields = [];
        const address = document.getElementById("id_address");
        if (address) { address.dataset.label = "Address"; fields.push(address); }
        const price = document.getElementById("id_price");
        if (price && !price.disabled) { price.dataset.label = "Price"; fields.push(price); }
        const approvalType = document.getElementById("id_approvalType");
        if (approvalType && !approvalType.disabled && approvalType.offsetParent !== null) {
            approvalType.dataset.label = "Approval Type";
            fields.push(approvalType);
        }

        if (!validateFields(fields)) return;
    }

    if (currentStep < 4) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
}

function validateFields(fields) {
    let hasError = false;
    fields.forEach(field => {
        if (!field) return;
        field.classList.remove("error");
        field.style.border = "";
        const oldError = field.parentElement.querySelector(".error-message");
        if (oldError) oldError.remove();

        if (field.name === "rentalIncome") {
            const lookValue = document.querySelector('input[name="look"]').value;
            if (lookValue !== "Rent") return;
        }

        if (!field.value || field.value.trim() === "") {
            hasError = true;
            field.classList.add("error");
            field.style.border = "2px solid #e53e3e";
            const fieldLabel = field.dataset.label || field.labels?.[0]?.innerText || field.placeholder || field.name || "This field";
            const error = document.createElement("span");
            error.className = "error-message";
            error.style.cssText = "color:#e53e3e; font-size:12px; display:block; margin-top:4px; font-weight:600;";
            error.innerText = `⚠ "${fieldLabel}" is required.`;
            field.parentElement.appendChild(error);
        }
    });
    return !hasError;
}

/* ==========================================================
   DYNAMIC FIELD LOGIC
========================================================== */
function updateConditionalFields(propertyType) {
    const allConditionalFields = document.querySelectorAll("#step-2 .conditional-fields");
    allConditionalFields.forEach((set) => {
        const isMatch = set.dataset.propertyType === propertyType;
        set.style.display = isMatch ? "block" : "none";
        set.classList.toggle("active-fieldset", isMatch);
        set.querySelectorAll("input, select, textarea").forEach((input) => {
            input.disabled = !isMatch;
        });
    });
}

function toggleReraSection(propertyType) {
    const reraSection = document.getElementById("reraSection");
    const approvalTypeSection = document.getElementById("approvalTypeSection");
    const amenitiesSection = document.getElementById("amenitiesSection");
    const landTypes = ["Lands", "Farm", "Developmentlands", "Disputelands", "Commerciallands"];
    const isLand = landTypes.includes(propertyType);

    const toggle = (section, show) => {
        if (!section) return;
        section.style.display = show ? "block" : "none";
        section.querySelectorAll("input, select, textarea").forEach(el => el.disabled = !show);
    };
    
    toggle(reraSection, !isLand);
    toggle(approvalTypeSection, !isLand);
    toggle(amenitiesSection, !isLand);
}

function toggleRentFields() {
    const lookValue = document.querySelector('input[name="look"]').value;
    const rentalFields = document.querySelectorAll('.rental-income-field');
    const depositFields = document.querySelectorAll('.deposit-field');
    const isRent = lookValue === 'Rent';

    const toggle = (fields, show) => {
        fields.forEach(field => {
            const input = field.querySelector('input');
            field.style.display = show ? 'block' : 'none';
            if (!show) input.value = '';
            input.disabled = !show;
        });
    };
    toggle(rentalFields, isRent);
    toggle(depositFields, isRent);
}

function toggleFurniture() {
    const lookValue = document.querySelector('input[name="look"]')?.value;
    const propertyValue = document.querySelector('input[name="selectProperty"]')?.value;
    const allowedProperties = ["House", "Flat", "Villa"];
    const furnitureFields = document.querySelectorAll(".furniture-field");
    const shouldShow = lookValue === "Rent" && allowedProperties.includes(propertyValue);

    furnitureFields.forEach(field => {
        const select = field.querySelector("select");
        field.style.display = shouldShow ? "block" : "none";
        if (!shouldShow) select.value = "";
        select.disabled = !shouldShow;
    });
}

/* ==========================================================
   INITIALIZATION
========================================================== */
document.addEventListener("DOMContentLoaded", () => {
    // Setup option buttons
    document.querySelectorAll(".option").forEach((button) => {
        button.addEventListener("click", () => {
            const fieldName = button.dataset.field;
            const fieldValue = button.dataset.value;
            const input = document.querySelector(`input[name="${fieldName}"]`);
            if (input) input.value = fieldValue;

            document.querySelectorAll(`.option[data-field="${fieldName}"]`).forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");

            if (fieldName === "selectProperty") {
                updateConditionalFields(fieldValue);
                toggleReraSection(fieldValue); 
                if (window.setRequiredFields) window.setRequiredFields(fieldValue);
                toggleFurniture();
            }
            if (fieldName === "look") {
                toggleRentFields();
                toggleFurniture();
            }
        });
    });

    // Step navigation
    showStep(currentStep);

    // Form submission
    const propertyForm = document.getElementById("addPropertyForm");
    if (propertyForm) {
        propertyForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const mediaError = document.getElementById("mediaError");
            if (mediaError) mediaError.style.display = "none";

            const imageInput = document.getElementById("id_image");
            const videoInput = document.getElementById("id_video");

            if (!imageInput.files.length || !videoInput.files.length) {
                if (mediaError) mediaError.style.display = "block";
                showStep(4);
                return;
            }

            const statusModal = document.getElementById("statusModal");
            const btnText = document.getElementById("btnText");
            if (statusModal) statusModal.classList.add("active");
            if (btnText) btnText.innerText = "⏳ Posting...";

            setTimeout(() => this.submit(), 800);
        });

        propertyForm.addEventListener("keydown", (e) => { if (e.key === "Enter") e.preventDefault(); });
    }

    // Media proxy handling
    const imageProxy = document.getElementById('id_image_proxy');
    if (imageProxy) {
        imageProxy.addEventListener('change', function() { distributeFiles(this.files); });
    }

    // Drag and Drop
    setupDragAndDrop('imageDropZone', 'id_image');
    setupDragAndDrop('videoDropZone', 'id_video');
    const docDropZone = document.getElementById('docDropZone');
    if (docDropZone) setupDragAndDrop('docDropZone', 'id_document');

    // Add More Images logic
    const addMoreBtn = document.getElementById("addMoreImages");
    if (addMoreBtn) {
        const hiddenImages = [
            document.getElementById("id_image2"),
            document.getElementById("id_image3"),
            document.getElementById("id_image4"),
            document.getElementById("id_image5")
        ].filter(el => el);

        let index = 0;
        addMoreBtn.addEventListener("click", () => {
            if (index < hiddenImages.length) {
                const field = hiddenImages[index];
                if (field.parentElement) field.parentElement.style.display = "block";
                index++;
                if (index === hiddenImages.length) addMoreBtn.style.display = "none";
            }
        });
    }

    // Custom Amenities
    const addAmenityBtn = document.getElementById("addAmenityBtn");
    const amenityInput = document.getElementById("id_custom_amenities_text");
    const amenityList = document.getElementById("addedAmenitiesList");
    if (addAmenityBtn && amenityInput && amenityList) {
        addAmenityBtn.addEventListener("click", () => {
            let value = amenityInput.value.trim();
            if (!value) return;
            value.split(",").map(a => a.trim()).filter(a => a).forEach(item => {
                let li = document.createElement("li");
                li.textContent = item;
                amenityList.appendChild(li);
            });
            amenityInput.value = "";
        });
    }

    // Video/Doc previews
    const videoInput = document.getElementById('id_video');
    if (videoInput) {
        videoInput.addEventListener('change', function() {
            const preview = document.getElementById('propVideoPreview');
            if (!preview) return;
            preview.innerHTML = '';
            if (this.files[0]) {
                const chip = document.createElement('div');
                chip.className = 'prop-file-chip';
                chip.innerHTML = `<i class="fa-solid fa-film"></i> <span>${this.files[0].name}</span> <i class="fa-solid fa-xmark" style="cursor:pointer; margin-left:8px; color:#ef4444;" onclick="clearMediaInput('id_video', 'propVideoPreview')"></i>`;
                preview.appendChild(chip);
            }
        });
    }

    const docInput = document.getElementById('id_document');
    if (docInput) {
        docInput.addEventListener('change', function() {
            const preview = document.getElementById('propDocPreview');
            if (!preview) return;
            preview.innerHTML = '';
            if (this.files[0]) {
                const chip = document.createElement('div');
                chip.className = 'prop-file-chip';
                chip.innerHTML = `<i class="fa-solid fa-file"></i> <span>${this.files[0].name}</span> <i class="fa-solid fa-xmark" style="cursor:pointer; margin-left:8px; color:#ef4444;" onclick="clearMediaInput('id_document', 'propDocPreview')"></i>`;
                preview.appendChild(chip);
            }
        });
    }

    // Nearby places live update
    const nearbyContainer = document.getElementById("nearby-container");
    if (nearbyContainer) {
        nearbyContainer.addEventListener("input", syncNearbyData);
    }
});

/* ==========================================================
   REQUIRED FIELDS MAP
========================================================== */
const requiredByProperty = {
    Plot: ["projectName", "extent", "units", "facing", "roadSize", "dimensions"],
    House: ["projectName", "extent", "units", "numberOfBHK", "numberOfFloors", "facing", "roadSize", "dimensions", "builtUpArea", "carpetArea", "openArea", "floorNo", "rentalIncome"],
    Flat: ["projectName", "communityType", "facing", "extent", "units", "builtUpArea", "carpetArea", "numberOfBHK", "floorNo"],
    Villa: ["projectName", "facing", "numberOfFloors", "numberOfBHK", "dimensions", "roadSize", "extent", "units", "builtUpArea", "openArea", "rentalIncome"],
    Farm: ["projectName", "extent", "units", "roadSize", "facing", "dimensions"],
    Lands: ["landType", "extent", "units", "soilType", "waterSource", "roadSize", "roadFacing"],
    Developmentlands: ["landType", "extent", "units", "soilType", "zone", "roadSize"],
    Disputelands: ["landType", "extent", "units", "soilType", "zone", "roadSize"],
    Commerciallands: ["landType", "extent", "units", "soilType", "waterSource", "roadSize", "roadFacing"]
};

window.setRequiredFields = function (propertyType) {
    document.querySelectorAll("[data-required]").forEach(el => el.removeAttribute("data-required"));
    const activeSet = document.querySelector("#step-2 .conditional-fields.active-fieldset");
    if (!activeSet) return;
    (requiredByProperty[propertyType] || []).forEach(fieldName => {
        const field = activeSet.querySelector(`[name="${fieldName}"]`);
        if (field) field.setAttribute("data-required", "true");
    });
};

/* ==========================================================
   GOOGLE MAPS INTEGRATION
========================================================== */
let map, marker, geocoder;

window.initMap = async function() {
    const defaultLocation = { lat: 17.385044, lng: 78.486671 };
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 13,
        mapId: "DEMO_MAP_ID"
    });
    geocoder = new google.maps.Geocoder();

    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    marker = new AdvancedMarkerElement({
        position: defaultLocation,
        map: map,
        gmpDraggable: true
    });

    marker.addListener("dragend", () => {
        geocoder.geocode({ location: marker.position }, (results, status) => {
            if (status === "OK" && results[0]) {
                const input = document.getElementById("search_location");
                if (input) input.value = results[0].formatted_address;
                updateMapFields(marker.position, results[0].formatted_address);
            }
        });
    });

    const { Autocomplete } = await google.maps.importLibrary("places");
    const searchInput = document.getElementById("search_location");
    if (!searchInput) return;

    const autocomplete = new Autocomplete(searchInput);
    autocomplete.bindTo("bounds", map);
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            if (searchInput.value) {
                geocoder.geocode({ address: searchInput.value }, (results, status) => {
                    if (status === "OK") {
                        const loc = results[0].geometry.location;
                        map.setCenter(loc); map.setZoom(16);
                        marker.position = loc;
                        updateMapFields(loc, results[0].formatted_address);
                    }
                });
            }
            return;
        }
        const loc = place.geometry.location;
        map.setCenter(loc); map.setZoom(16);
        marker.position = loc;
        updateMapFields(loc, place.formatted_address || searchInput.value);
    });

    searchInput.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); google.maps.event.trigger(autocomplete, "place_changed"); } });
    updateMapFields(defaultLocation, "");
};

function updateMapFields(location, address) {
    const lat = typeof location.lat === 'function' ? location.lat() : location.lat;
    const lng = typeof location.lng === 'function' ? location.lng() : location.lng;
    const latInput = document.getElementById("id_latitude");
    const lngInput = document.getElementById("id_longitude");
    const locInput = document.getElementById("id_location");
    const urlInput = document.getElementById("id_locationUrl");

    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;
    if (locInput) locInput.value = address || "";
    if (urlInput) urlInput.value = `https://www.google.com/maps?q=${lat},${lng}`;
}
