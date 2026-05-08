function toggleFilters() {
        const box = document.getElementById("filterBox");
        box.classList.toggle("open");
        if (box.classList.contains("open")) {
          setTimeout(initAutocomplete, 100);
        }
      }

      function applyQuickFilter(type) {
        const url = new URL(window.location.href);

        // set Sell / Rent
        url.searchParams.set("look", type);

        // reload with filter
        window.location.href = url.toString();
      }

      /* Highlight active button */
      document.addEventListener("DOMContentLoaded", () => {
        const params = new URLSearchParams(window.location.search);
        const look = params.get("look");

        document.querySelectorAll(".quick-filter-btn").forEach((btn) => {
          if (btn.dataset.type === look) {
            btn.classList.add("active");
          }
        });
      });

      function toggleSave(event, id, btn) {
        event.stopPropagation();
        event.preventDefault();

        fetch(`/save/${id}/`, { method: "GET" })
          .then((res) => res.json())
          .then((data) => {
            const icon = btn.querySelector("i");

            if (data.status === "saved") {
              btn.classList.add("saved");
              icon.classList.replace("bi-bookmark", "bi-bookmark-fill");
            } else {
              btn.classList.remove("saved");
              icon.classList.replace("bi-bookmark-fill", "bi-bookmark");
            }
          });
      }
    
      // IS_AUTHENTICATED is now provided by the template in a global script block

    
      function goToProperty(event, propertyId) {
        // ❌ Ignore clicks on buttons / actions
        if (
          event.target.closest("button") ||
          event.target.closest(".share-wrapper") ||
          event.target.closest(".share-box") ||
          event.target.closest(".save-btn") ||
          event.target.closest(".contact-btn-main") ||
          event.target.closest(".chat-inline-btn") ||
          event.target.closest("a")
        ) {
          return;
        }

        // 🔐 Not logged in → login

        // ✅ Logged in → property detail
        window.location.href = `/property/${propertyId}`;
      }
   
      function handleContact(event, userId, propertyId, phone) {
        event.stopPropagation();
        event.preventDefault();

        // 🔐 NOT LOGGED IN → LOGIN
        if (!IS_AUTHENTICATED) {
          window.location.href = LOGIN_URL;
          return;
        }

        // ✅ LOGGED IN → CALL EXISTING FUNCTION
        propertyLead(event, userId, propertyId, phone);
      }
   
      document.addEventListener("click", function (e) {
        /* SHARE BUTTON CLICK */
        const shareBtn = e.target.closest(".share-btn");
        if (shareBtn) {
          e.stopPropagation();

          const wrapper = shareBtn.closest(".share-wrapper");
          const box = wrapper.querySelector(".share-box");

          // Close other share boxes
          document.querySelectorAll(".share-box").forEach((b) => {
            if (b !== box) b.style.display = "none";
          });

          // Toggle current
          box.style.display = box.style.display === "flex" ? "none" : "flex";
          return;
        }

        /* SHARE ITEM CLICK */
        const item = e.target.closest(".share-item");
        if (item) {
          e.stopPropagation();

          const type = item.dataset.type;
          const wrapper = item.closest(".share-wrapper");
          const propertyId = wrapper.dataset.propertyId;
          const url = `${window.location.origin}/property/${propertyId}/`;

          switch (type) {
            case "whatsapp":
              window.open(`https://wa.me/?text=${encodeURIComponent(url)}`);
              break;
            case "telegram":
              window.open(
                `https://t.me/share/url?url=${encodeURIComponent(url)}`,
              );
              break;
            case "facebook":
              window.open(
                `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
              );
              break;
            case "copy":
              navigator.clipboard.writeText(url);
              alert("Link copied");
              break;
          }

          wrapper.querySelector(".share-box").style.display = "none";
          return;
        }

        /* CLICK OUTSIDE → CLOSE ALL */
        document.querySelectorAll(".share-box").forEach((b) => {
          b.style.display = "none";
        });
      });
    
      function handleProfileClick(el, event) {
        event.stopPropagation();
        event.preventDefault();

        const role = el.dataset.role;
        const userId = el.dataset.userId;

        if (role === "OWNER") return;

        window.location.href = `/user/${userId}/`;
      }
    
      function shareProfile(id) {
        if (navigator.share) {
          navigator.share({
            title: "User Profile",
            text: "Check out this profile",
            url: `${window.location.origin}/property/${id}`,
          });
        } else {
          navigator.clipboard.writeText(window.location.href);
          alert("Profile link copied!");
        }
      }
   
      let autocompleteInitialized = false;

      function initAutocomplete() {
        if (autocompleteInitialized) return;

        const input = document.getElementById("locationSearch");
        if (!input) return;

        // 🔥 google MUST exist here
        if (!window.google || !google.maps || !google.maps.places) {
          console.warn("Google Maps not ready yet");
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
            if (
              !city &&
              component.types.includes("administrative_area_level_2")
            ) {
              city = component.long_name;
            }
          });

          input.value = city;
          console.log("City selected:", city);
        });

        autocompleteInitialized = true;
      }

      // 🔥 this is called AFTER Google loads
      function onGoogleMapsLoaded() {
        // Desktop → visible immediately
        if (window.innerWidth > 768) {
          initAutocomplete();
        }
      }
   document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const look = params.get("look");

  document.querySelectorAll(".quick-filter-btn").forEach((btn) => {
    if (btn.dataset.type === look) {
      btn.classList.add("active");
    }
  });
});